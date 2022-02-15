import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from datetime import datetime
import mysql.connector


def log(logfile, message):
    timestamp_format = '%H:%M:%S-%h-%d-%Y'
    # Hour-Minute-Second-MonthName-Day-Year
    now = datetime.now()  # get current timestamp
    timestamp = now.strftime(timestamp_format)
    with open(logfile, "a") as f:
        f.write('[' + timestamp + ']: ' + message + '\n')
        print(message)


def transform():
    log(logfile, "-------------------------------------------------------------")
    log(logfile, "Inicia Fase De Transformacion")
    df_customers = pd.read_sql_query("""SELECT 
        CustomerId,
        FirstName, 
        LastName, 
        COALESCE(Company, 'N/A') as Company,
        Address, 
        City, 
        COALESCE(State, 'N/A') as State, 
        Country, COALESCE(PostalCode, 'N/A') as PostalCode, 
        COALESCE(Phone, 'N/A') as Phone, 
        COALESCE(Fax, 'N/A') as Fax, 
        Email  
        FROM customers;""", con=engine.connect())
    df_artists = pd.read_sql_query("""SELECT ArtistId, Name as NameArtist FROM artists;""", con=engine.connect())
    df_albums = pd.read_sql_query("""SELECT AlbumId, Title as TitleAlbum FROM albums;""", con=engine.connect())
    df_genres = pd.read_sql_query("""SELECT GenreId, Name as NameGenre FROM genres;""", con=engine.connect())
    df_employees = pd.read_sql_query("""SELECT 
        EmployeeId, 
        LastName, 
        FirstName, 
        Title, 
        BirthDate, 
        HireDate, 
        Address, 
        City, 
        State, 
        Country, 
        PostalCode, 
        Phone, 
        Fax, 
        Email 
        FROM employees;""", con=engine.connect())
    df_invoice_items = pd.read_sql_query("""SELECT InvoiceLineId, UnitPrice, Quantity FROM invoice_items;""",
                                         con=engine.connect())
    df_playlists = pd.read_sql_query("""SELECT PlaylistId, Name as NamePlaylist FROM playlists;""",
                                     con=engine.connect())
    df_location = pd.read_sql_query("""SELECT 
        CustomerId as LocationId, 
        Address, 
        City, 
        COALESCE(State, 'N/A') as State, 
        Country, 
        COALESCE(PostalCode, 'N/A') as PostalCode 
        FROM customers;""", con=engine.connect())

    log(logfile, "Finaliza Fase De Transformacion")
    log(logfile, "-------------------------------------------------------------")
    return df_albums, df_artists, df_customers, df_employees, df_genres, df_invoice_items, df_location, df_playlists

def load():
    """ Connect to the MYSQL Workbench database server """
    conn_string = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='1234',
        port='3306',
        database='dw_sales_music'
    )
    db = create_engine(conn_string)
    conn = db.connect()
    try:
        log(logfile, "-------------------------------------------------------------")
        log(logfile, "Inicia Fase De Carga")
        df_customers.to_sql('dim_customer', con=conn, if_exists='append', index=False)
        df_employees.to_sql('dim_employees', con=conn, if_exists='append', index=False)
        df_genres.to_sql('dim_genres', con=conn, if_exists='append', index=False)
        df_albums.to_sql('dim_albums', con=conn, if_exists='append', index=False)
        df_artists.to_sql('dim_artist', con=conn, if_exists='append', index=False)
        df_playlists.to_sql('dim_playlist', con=conn, if_exists='append', index=False)
        df_location.to_sql('dim_location', con=conn, if_exists='append', index=False)
        df_invoice_items.to_sql('dim_invoice_items', con=conn, if_exists='append', index=False)
        conn = mysql.connector.connect(conn_string)
        conn.autocommit = True
        conn.cursor()
        log(logfile, "Finaliza Fase De Carga")
        log(logfile, "-------------------------------------------------------------")
    except (Exception, mysql.connector.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def extract():
    log(logfile, "--------------------------------------------------------")
    log(logfile, "Inicia Fase De Extraccion")
    metadata = MetaData()
    metadata.create_all(engine)
    log(logfile, "Finaliza Fase De Extraccion")
    log(logfile, "--------------------------------------------------------")


if __name__ == '__main__':
    logfile = "ETL_logfile.txt"
    log(logfile, "Trabajo iniciado.")
    engine = create_engine("sqlite:///chinook.db")
    extract()
    (df_albums,
     df_artists,
     df_customers,
     df_employees,
     df_genres,
     df_invoice_items,
     df_location,
     df_playlists) = transform()
    load()
    log(logfile, " Trabajo finalizado.")