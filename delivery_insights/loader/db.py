from configparser import ConfigParser

import pandas as pd
import psycopg2
from sqlalchemy import create_engine


class Database:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path

    def parser(self, section="postgresql") -> dict:
        """
        Parse arguments from database ini file

        :param section:
        :return:
        """
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(self.config_file_path)

        # get section, default to postgresql
        db = {}

        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception(
                "Section {0} not found in the {1} file".format(
                    section, self.config_file_path
                )
            )

        return db

    def test_connection(self) -> None:
        """
        Function to test postgres connection

        :return:
        """
        """Connect to the PostgreSQL database server"""
        conn = None
        credentials = self.parser()
        try:
            # connect to the PostgreSQL server
            print("Connecting to the PostgreSQL database...")
            conn = psycopg2.connect(**credentials)

            # create a cursor
            cur = conn.cursor()

            # execute a statement
            print("PostgreSQL database version:")
            cur.execute("SELECT version()")

            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            print(db_version)

            # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print("Database connection closed.")

    def execute_query(self, query: str) -> None:
        """
        Function to execute string query

        :param query:
        :return:
        """
        if query is None:
            raise Exception("You need to specify your query")

        conn = None
        credentials = self.parser()
        try:
            print("Execute query into database")
            conn = psycopg2.connect(**credentials)

            cur = conn.cursor()
            cur.execute(query)
            cur.close()

            conn.commit()
        except Exception as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def select_query(self, query: str) -> None:
        """
        Execute select query

        :param query:
        :return:
        """
        if query is None:
            raise Exception("You need to specify your query")

        conn = None
        credentials = self.parser()
        try:
            print("Select query execution")
            conn = psycopg2.connect(**credentials)
            cur = conn.cursor()

            cur.execute(query)

            print("The number of rows: ", cur.rowcount)

            cur.close()

            conn.commit()
        except Exception as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def insert_df_into_table(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Using sqlAlchemy append dataframe to postgres table

        :param df:
        :param table_name:
        :return:
        """
        if len(df) == 0:
            print("Dataframe is empty.")
            return
        if table_name is None:
            raise Exception("Please add a table name to insert into.")

        conn = None
        credentials = self.parser()

        try:
            conn = create_engine(
                f"""postgresql+psycopg2://{credentials['user']}:{credentials['password']}@{credentials['host']}:
                5432/{credentials['database']}"""
            )

            df.to_sql(table_name, conn, index=False, if_exists="replace")
            conn.commit()
        except Exception as error:
            print(error)
