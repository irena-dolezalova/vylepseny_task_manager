from mysql.connector import connect, Error
import pytest

db_name = "test_task_manager"
tb_name = "test_ukoly"


@pytest.fixture(scope = "function")
def pripojeni_db():
    try:
        conn = connect(
            host="localhost",
            user= "root",
            password = ""
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        sql_create_tb = f"""
                CREATE TABLE IF NOT EXISTS {tb_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(50) NOT NULL,      
                popis VARCHAR(255) NOT NULL,
                stav ENUM ("nezahájeno", "hotovo", "probíhá") NOT NULL DEFAULT "nezahájeno",
                datum_vytvoreni DATE NOT NULL)
                """
        cursor.execute(sql_create_tb)
        cursor.execute(f"TRUNCATE TABLE {tb_name}")
        conn.commit()
    except Error as e:
        print(f"\nChyba při připojování k databázi: {e}")
    
    yield conn, cursor
    cursor.execute(f"DROP DATABASE {db_name}")
    cursor.close 
    conn.close()


def test_pridat_ukol(pripojeni_db):
    conn, cursor = pripojeni_db
    data_insert = ("zahrada", "posekat trávník", "2025-02-15")     
    sql_insert = f"INSERT INTO {tb_name} (nazev, popis, datum_vytvoreni) VALUES (%s, %s, %s)"
    cursor.execute(sql_insert, data_insert)
    conn.commit()
    
    data_test = (data_insert[0], )
    sql_test = f"SELECT * FROM {tb_name} WHERE nazev = %s"
    cursor.execute(sql_test, data_test)
    result = cursor.fetchone()
    assert result is not None, "Záznam nebyl vložen do tabulky."
    assert result[1] == data_insert[0], "Název úkolu není správný."
    assert result[2] == data_insert[1], "Popisek není správný."


def test_pridat_ukol_invalid_data(pripojeni_db):    
    conn, cursor = pripojeni_db 
    with pytest.raises(Error, match = "Data too long for column"):
        sql_insert = f"INSERT INTO {tb_name} (nazev, popis, datum_vytvoreni) VALUES (%s, %s, %s)"
        data_insert = ("a" * 256, "pokusný popisek", "2025-02-15")
        cursor.execute(sql_insert, data_insert)
        conn.commit()
    

def test_aktualizovat_ukol(pripojeni_db):
    conn,cursor = pripojeni_db    
    sql_insert = f"INSERT INTO {tb_name} (nazev, popis, datum_vytvoreni) VALUES (%s, %s, %s)"
    data_insert = ("zahrada", "posekat trávník", "2025-02-15")    
    cursor.execute(sql_insert, data_insert)
    
    sql_update = f"UPDATE {tb_name} SET popis = %s WHERE nazev = %s"
    data_update = ("koupit osivo", data_insert[0])
    cursor.execute(sql_update, data_update)
    conn.commit()

    sql_test = f"SELECT popis FROM {tb_name} WHERE nazev = %s"
    data_test = (data_insert[0], )
    cursor.execute(sql_test, data_test)
    result = cursor.fetchone()
    print(result)
    assert result[0] == data_update[0], "Popisek nebyl správně aktualizován."


def test_aktualizovat_ukol_invalid_data(pripojeni_db):
    conn,cursor = pripojeni_db    
    with pytest.raises(Error, match = "Data truncated for column"):     
        sql_insert = f"INSERT INTO {tb_name} (nazev, popis, datum_vytvoreni) VALUES (%s, %s, %s)"
        data_insert = ("zahrada", "posekat trávník", "2025-02-15")   
        cursor.execute(sql_insert, data_insert)
        
        sql_update = f"UPDATE {tb_name} SET stav = %s WHERE nazev = %s"
        data_update = ("neznámý", data_insert[0])
        cursor.execute(sql_update, data_update)
        conn.commit()


def test_odstranit_ukol(pripojeni_db):
    conn, cursor = pripojeni_db    
    sql_insert = f"INSERT INTO {tb_name} (nazev, popis, datum_vytvoreni) VALUES (%s, %s, %s)"
    data_insert = ("zahrada", "posekat trávník", "2025-02-15")   
    cursor.execute(sql_insert, data_insert)
    conn.commit()

    sql_delete = f"DELETE FROM {tb_name} WHERE nazev = %s"
    data_delete = (data_insert[0], )   
    cursor.execute(sql_delete, data_delete)
    conn.commit()

    sql_test = f"SELECT * FROM {tb_name} WHERE nazev = %s"
    data_test = (data_insert[0], )
    cursor.execute(sql_test, data_test)
    result = cursor.fetchone()
    assert result is None, "Záznam nebyl správně smazán."


def test_odstranit_ukol_nonexistent_data(pripojeni_db):
    conn, cursor = pripojeni_db    
    sql_select = f"SELECT COUNT(*) FROM {tb_name}"
    cursor.execute(sql_select)
    initial_count = cursor.fetchone()[0]
    
    sql_delete = f"DELETE FROM {tb_name} WHERE id = %s"
    data_delete = (1, )
    cursor.execute(sql_delete, data_delete)
    conn.commit()

    sql_test = f"SELECT COUNT(*) FROM {tb_name}"
    cursor.execute(sql_test)
    final_count = cursor.fetchone()[0]
    assert initial_count == final_count, "Mazání neexistujícího záznamu změnilo stav databáze."