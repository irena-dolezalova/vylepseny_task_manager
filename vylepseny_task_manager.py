from mysql.connector import connect, Error
from getpass import getpass
from datetime import date

db_name = "task_manager"
tb_name = "ukoly"

def prihlasovaci_udaje ():
    while True:
        try:
            with connect (
                user = getpass("Zadejte uživatele: "),
                password = getpass("Zadejte heslo:")
            ) as conn:
                return conn._user, conn._password
        except Error as e:
            print(f"\nNesprávné přihlašovací údaje, zadejte prosím znovu. {e}")
        

def vytvoreni_databaze():
    sql_create_db = f"CREATE DATABASE {db_name}"
    try:
        with connect (host = "localhost", user = user, password = password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                if (db_name, ) in cursor.fetchall():
                    print(f"Databáze '{db_name}' je k dispozici.")
                else:
                    cursor.execute(sql_create_db)
                    print(f"Databáze '{db_name}' byla vytvořena.")        
    except Error as e:
        print(f"\nChyba při vytváření databáze: {e}")
        ukonci_program()    


def pripojeni_db():  
    try:
        conn = connect(host = "localhost", user = user, password = password, database = "task_manager")
        return conn         
    except Error as e:
        print(f"\nChyba při připojování k databázi: {e}")
        ukonci_program()

 
def vytvoreni_tabulky():           
    sql_create_tb = f"""
        CREATE TABLE IF NOT EXISTS {tb_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nazev VARCHAR(50) NOT NULL,      
        popis VARCHAR(255) NOT NULL,
        stav ENUM ("probíhá", "hotovo", "nezahájeno") NOT NULL DEFAULT "nezahájeno",
        datum_vytvoreni DATE NOT NULL)
        """
    try:
        with pripojeni_db() as conn:   
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")  
                if (tb_name, ) in cursor.fetchall():
                    print(f"Tabulka '{tb_name}' je k dispozici.")
                else:
                    cursor.execute(sql_create_tb)
                    print(f"Tabulka '{tb_name}' byla vytvořena.") 
    except Error as e:
        print(f"\nChyba při vytváření tabulky: {e}")                        
    

def pridat_ukol():    
    while True:
        try:
            task_name = input("\nZadejte název úkolu: ").strip().capitalize()
            task_description = input("Zadejte popis úkolu: ").strip().lower()
        except EOFError:
            print("\nPrázdný vstup, zadejte prosím znovu.")
            continue
        except KeyboardInterrupt:
            print("\n\nPrázdný vstup, zadejte prosím znovu.")
            continue      

        if task_name and task_description:
            sql_insert = f"INSERT INTO {tb_name} (nazev, popis, datum_vytvoreni) VALUES (%s, %s, %s)"
            data = (task_name, task_description, date.today())
            try:
                with pripojeni_db() as conn:
                    with conn.cursor() as cursor:                       
                        cursor.execute(sql_insert,data)
                        conn.commit()
                        print(f"\nÚkol '{task_name}' byl přidán.")
                        break
            except Error as e:
                print(f"\nChyba při ukládání úkolu: {e}")
                ukonci_program()
        else:
            print("\nPrázdný vstup, zadejte prosím znovu.")


def zobrazit_ukoly(filter = False):  
    if not filter:
       sql_select = f"SELECT * FROM {tb_name}"  
    else:        
        filter_1 = "probíhá"
        filter_2 = "nezahájeno"
        sql_select = f"SELECT * FROM {tb_name} WHERE stav = '{filter_1}' OR stav = '{filter_2}'"
        
    try:
        with pripojeni_db() as conn:
            filter_completed = "hotovo"
            sql_completed_tasks = f"SELECT * FROM {tb_name} WHERE stav = '{filter_completed}'"
            with conn.cursor() as cursor:
                cursor.execute(sql_select)
                tasks = cursor.fetchall()                
                cursor.execute(sql_completed_tasks) 
                tasks_completed = cursor.fetchall()                         
            if tasks: 
                print("\nSeznam úkolů:")
                for task in tasks:            
                    print(f"{task[0]:4d}. úkol: {task[1]} ({task[2]}), status - {task[3]}")
            elif tasks_completed:
                print("\nVšechny úkoly jsou hotové.")
            else:                                      
                print("\nSeznam úkolů je prázdný.")
            return tasks      
    except Error as e:
        print(f"\nChyba při zobrazování úkolů: {e}")
        ukonci_program() 


def aktualizovat_ukol():
    task_found = False
    while not task_found:
        tasks = zobrazit_ukoly(filter = True)
        if len(tasks) >1:                 
            try:                
                task_id = int(input("\nZadejte číslo úkolu, který chcete aktualizovat: ").strip())
                for task in tasks:
                    if task_id == task[0]:
                        task_found = task
                        break
                if task_found:
                    break                
            except ValueError:
                print("\nNeplatná volba, zadejte prosím znovu.")
                continue
            except EOFError:
                print("\nNeplatná volba, zadejte prosím znovu.")
                continue
            except KeyboardInterrupt:
                print("\n\nNeplatná volba, zadejte prosím znovu.")
                continue
            else:
                print("\nNeplatná volba, zadejte prosím znovu.")
                continue
        elif len(tasks) == 1:
            task_id = tasks[0][0]
            task_found = tasks[0]                   
        else:
            break

    while task_found:
        try: 
            if task_found[3] == "nezahájeno":
                print("\nStav úkolu můžete změnit na:")
                print("1. probíhá")
                print("2. hotovo")
                choice = int(input("Vyberte možnost (1-2): ").strip()) 
            else:
                print("\nStav úkolu můžete změnit na'hotovo', souhlasíte?")
                print("1. ano")
                print("2. ne")
                choice_yes_no = int(input("Vyberte možnost (1-2): ").strip())
                if choice_yes_no == 1:
                    choice = 2
                elif choice_yes_no == 2:
                    print("\nStav úkolu nebyl nezměněn.")
                    break
                else:
                    print("\nNeplatná volba, zadejte prosím znovu.")
                    continue
        except ValueError:
            print("\nNeplatná volba, zadejte prosím znovu.")
            continue
        except EOFError:
            print("\nNeplatná volba, zadejte prosím znovu.")
            continue
        except KeyboardInterrupt:
            print("\n\nNeplatná volba, zadejte prosím znovu.")
            continue       
        else:
            if choice == 1 or choice == 2:
                sql_update = f"UPDATE {tb_name} SET stav = %s WHERE id = %s"
                data = (choice, task_id)
                try:             
                    with pripojeni_db() as conn:
                        with conn.cursor() as cursor:                                                 
                            cursor.execute(sql_update, data)
                            conn.commit()
                            print("\nStav úkolu byl změněn.")                                
                            break
                except Error as e:
                        print(f"\nChyba při aktualizaci úkolu: {e}")
                        ukonci_program()
            else:
                print("\nNeplatná volba, zadejte prosím znovu.")
                continue                
      

def odstranit_ukol():
    task_found = False
    while not task_found:
        tasks = zobrazit_ukoly()
        try:
            if len(tasks) > 1:                           
                task_id = int(input("\nZadejte číslo úkolu, který chcete smazat: ").strip())
                for task in tasks:
                    if task_id == task[0]:
                        task_found = task
                        break
                if task_found:
                    break                                
            elif len(tasks) == 1:
                while True:
                    print("\nV seznamu úkolů je pouze tento úkol, chcete jej smazat?")
                    print("1. ano")
                    print("2. ne")
                    choice_yes_no = int(input("Vyberte možnost (1-2): ").strip())
                    if choice_yes_no == 1:
                        task_id = tasks[0][0] 
                        task_found = tasks[0]
                        break                    
                    elif choice_yes_no == 2:
                        print("\nÚkol nebyl odstraněn.") 
                        task_found = "not delete"
                        break
                    else:
                        print("\nNeplatná volba, zadejte prosím znovu.")
                        continue
            else:
                break   
        except ValueError:
                print("\nNeplatná volba, zadejte prosím znovu.")
                continue
        except EOFError:
            print("\nNeplatná volba, zadejte prosím znovu.")
            continue
        except KeyboardInterrupt:
            print("\n\nNeplatná volba, zadejte prosím znovu.")
            continue                                               
        else:
            print("\nNeplatná volba, zadejte prosím znovu.")
            continue                 

    if task_found and task_found != "not delete":
        try:
            with pripojeni_db() as conn:
                sql_delete = f"DELETE FROM {tb_name} WHERE id = %s"
                data = (task_id, )
                with conn.cursor() as cursor:
                    cursor.execute(sql_delete, data)
                    conn.commit()
                    print("\nÚkol byl odstraněn.")                         
        except Error as e:
            print(f"\nChyba při odstraňování úkolu: {e}")
            ukonci_program()
            
            
def ukonci_program():
    print("\nKonec programu.\nNa shledanou!")
    exit()
    
                
def hlavni_menu():
    print("\n\nVítejte!\n")
    while True:    
        print("\nSprávce úkolů - Hlavní menu")
        print("1. Přidat nový úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Konec programu")

        try:
            choice = int(input("Vyberte možnost (1-5): ").strip())                                
        except ValueError:
            print("\nNeplatná volba, zadejte prosím znovu.")
            continue
        except EOFError:
            print("\nNeplatná volba, zadejte prosím znovu.")
            continue
        except KeyboardInterrupt:
            print("\n\nNeplatná volba, zadejte prosím znovu.")
            continue
            
        if choice == 1:
            pridat_ukol()
        elif choice == 2:
            zobrazit_ukoly()
        elif choice == 3:
            aktualizovat_ukol()
        elif choice == 4:
            odstranit_ukol()
        elif choice == 5:
            ukonci_program()
        else:
            print("\nNeplatná volba, zadejte prosím znovu.")

user, password = prihlasovaci_udaje() 
vytvoreni_databaze()
vytvoreni_tabulky()
hlavni_menu()