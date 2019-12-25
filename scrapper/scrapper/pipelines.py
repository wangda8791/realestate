# -*- coding: utf-8 -*-

import sqlite3


class ScrapperPipeline(object):

    def __init__(self):
        try:
            self.create_connection()
            self.create_table()
        except:
            print('Init error')

    def create_connection(self):
        self.con = sqlite3.connect('realestate.db')
        self.cur = self.con.cursor()

    def create_table(self):
        self.cur.execute("""create table realestate_tb (
                        link text,
                        address text,
                        description text,
                        image_url text,
                        owner_name text,
                        owner_contact text,
                        active_search text
                    )""")

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        self.cur.execute("""insert into realestate_tb values (?,?,?,?,?,?,?)""", (
            item['link'],
            item['address'],
            item['description'],
            item['image_url'],
            item['owner_name'],
            item['owner_contact'],
            item['active_search']
        ))
        self.con.commit()
