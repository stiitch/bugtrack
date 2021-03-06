#------------------------------------------------------------------------------
# DbSqlite.py
# Bugrack database module that uses SQLite for storage.
#------------------------------------------------------------------------------

import sqlite3
import string
from ConfigParser import SafeConfigParser
import Db

class DbSqlite(Db.Db):

    #--------------------------------------------------------------------------
    # database maintenance
    #--------------------------------------------------------------------------
    SCHEMA_GAMES = [
            ['time',            'INTEGER'],  # Timestamp in epoch seconds
            ['teamAwhite',      'TEXT'],     # Winner - White player
            ['teamAwhiteRating','INTEGER'],  # Winner - White player rating
            ['teamAwhiteRD',    'INTEGER'],  # Winner - White player RD
            ['teamAblack',      'TEXT'],     # Winner - Black player
            ['teamAblackRating','INTEGER'],  # Winner - Black player rating
            ['teamAblackRD',    'INTEGER'],  # Winner - Black player RD
            ['teamBwhite',      'TEXT'],     # Loser  - White player
            ['teamBwhiteRating','INTEGER'],  # Loser  - White player rating
            ['teamBwhiteRD',    'INTEGER'],  # Loser  - White player RD
            ['teamBblack',      'TEXT'],     # Loser  - Black player
            ['teamBblackRating','INTEGER'],  # Loser  - Black player rating
            ['teamBblackRD',    'INTEGER']]  # Loser  - Black player RD
    SCHEMA_PLAYERS = [
            ['name',  'TEXT'],     # Name
            ['rating','INTEGER'],  # Rating
            ['rd',    'INTEGER'],  # Rd
            ['time',  'INTEGER']]  # Timestamp of last game played

    # Database configuration and initialization ------------------------------
    def createDatabase(self):
        print '\tDropping old tables'
        cmd = 'DROP TABLE IF EXISTS ' + self.config.get('Database','table_games') + ';'
        self.c.execute(cmd)
        cmd = 'DROP TABLE IF EXISTS ' + self.config.get('Database','table_players') + ';'
        self.c.execute(cmd)
        print '\tCreating new tables'

        # Games
        cmd = 'CREATE TABLE ' + self.config.get('Database','table_games') + ' (id INTEGER PRIMARY KEY, '
        for field in self.SCHEMA_GAMES:
            cmd += field[0] + ' ' + field[1] + ', '
        cmd = cmd[:-2]
        cmd += ');'
        self.c.execute(cmd)

        # Players
        cmd = 'CREATE TABLE ' + self.config.get('Database','table_players') + ' (id INTEGER PRIMARY KEY, '
        for field in self.SCHEMA_PLAYERS:
            cmd += field[0] + ' ' + field[1] + ', '
        cmd = cmd[:-2]
        cmd += ');'
        self.c.execute(cmd)
        self.conn.commit()

    def genDBEntry(self, schema, table, db_values):
        cmd = 'INSERT INTO ' + table + '('
        #for field in self.SCHEMA_GAMES:
        for field in schema:
            cmd += field[0] + ','
        cmd = cmd[:-1]
        cmd += ') VALUES ('
        for value in db_values:
            cmd += str(value) + ','
        cmd = cmd[:-1]
        cmd += ');'
        self.c.execute(cmd)
        self.conn.commit()

    def importGamesDat(self, filename):
        print 'Importing game data from [' + filename + ']...'
        f = open(filename,'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            time             = line[:10]
            teamAwhite       = '\'' + line[11:].split(",")[0].split('(')[0] + '\''
            teamAwhiteRating = line[11:].split(",")[0].split('(')[1].split(')')[0]
            teamAwhiteRD     = 350
            teamAblack       = '\'' + line[11:].split(',')[1].split('(')[0] + '\''
            teamAblackRating = line[11:].split(',')[1].split('(')[1].split(')')[0]
            teamAblackRD     = 350
            teamBwhite       = '\'' + line[11:].split(',')[1].split('>')[1].split('(')[0][1:] + '\''
            teamBwhiteRating = line[11:].split(',')[1].split('>')[1].split('(')[1].split(')')[0]
            teamBwhiteRD     = 350
            teamBblack       = '\'' + line[11:].split(',')[2].split('(')[0] + '\''
            teamBblackRating = line[11:].split(',')[2].split('(')[1].split(')')[0]
            teamBblackRD     = 350
            self.genDBEntry(self.SCHEMA_GAMES, self.config.get('Database','table_games'), \
                [time, \
                 teamAwhite, teamAwhiteRating, teamAwhiteRD, \
                 teamAblack, teamAblackRating, teamAblackRD, \
                 teamBwhite, teamBwhiteRating, teamBwhiteRD, \
                 teamBblack, teamBblackRating, teamBblackRD])

    def importPlayersDat(self, filename):
        print 'Importing player data from [' + filename + ']...'
        f = open(filename,'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            tokens = line[:-1].split(" ")
            t      = tokens[len(tokens)-1]
            rd     = tokens[len(tokens)-2]
            rating = tokens[len(tokens)-3]
            player = '\''
            for i in range(len(tokens) - 3):
                player += tokens[i] + ' '
            player = player[:-1] + '\''
            self.genDBEntry(self.SCHEMA_PLAYERS, self.config.get('Database','table_players'), [player,rating,rd,t])

    #--------------------------------------------------------------------------
    # general info
    #--------------------------------------------------------------------------
    # return list of players
    def getPlayerList(self):
        self.c.execute('SELECT name from ' + self.config.get('Database','table_players') + ';')
        return [ row for row in self.c.fetchall() ]

    def createNewPlayer(self, name, rating):
        cmd = 'INSERT into ' + self.config.get('Database','table_players') + \
              ' (name,rating,rd) VALUES (\'' + name + '\',' + str(rating) + ',350);'
        self.c.execute(cmd)
        self.conn.commit()

    #--------------------------------------------------------------------------
    # get player stats
    #--------------------------------------------------------------------------
    # get the player's rating
    def getPlayerRating(self, name):
        self.c.execute('SELECT rating from ' + self.config.get('Database','table_players') + \
                       ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0][0]

    # get the player's RD
    def getPlayerRD(self, name):
        self.c.execute('SELECT rd from ' + self.config.get('Database','table_players') + \
                       ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0][0]

    # return a list [rating, RD]
    def getPlayerStats(self, name):
        self.c.execute('SELECT rating,rd from ' + self.config.get('Database','table_players') + \
                       ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0]

    #--------------------------------------------------------------------------
    # set player stats
    #--------------------------------------------------------------------------
    def setPlayerRating(self, name, r):
        cmd = 'UPDATE ' + self.config.get('Database','table_players') + \
              ' set rating = ' + str(r) + ' WHERE (name = \'' + name + '\');'
        self.c.execute(cmd)
        self.conn.commit()

    def setPlayerRD(self, name, rd):
        cmd = 'UPDATE ' + self.config.get('Database','table_players') + \
              ' set rd = ' + str(rd) + ' WHERE (name = \'' + name + '\');'
        self.c.execute(cmd)
        self.conn.commit()

    def setPlayerStats(self, name, listStats):
        print 'setPlayerStats() not implemented!'

    #--------------------------------------------------------------------------
    # game stats
    #--------------------------------------------------------------------------

    # returns a row from the database - currently we define row as:
    # [date, teamAwhitePlayer, teamAwhitePlayerRating,
    #        teamAblackPlayer, teamAblackPlayerRating,
    #        teamBwhitePlayer, teamBwhitePlayerRating,
    #        teamBblackPlayer, teamBblackPlayerRating]
    #
    # where, by convention, teamA are the winners, teamB are the losers
    #
    # (change this comment if the db schema changes please)
    def getGames(self, since):
        self.c.execute('SELECT * from ' + self.config.get('Database','table_games') + \
                       ' WHERE (time > ' + str(since) + ');')
        return [ row for row in self.c.fetchall() ]

    # retrieve all games that had player involved in it
    def getGamesByPlayer(self, name, since):
        print 'getGamesByPlayer() not implemented!'

    def recordGame(self, t, \
                   teamAWhite, tawRating, tawRd, \
                   teamABlack, tabRating, tabRd, \
                   teamBWhite, tbwRating, tbwRd, \
                   teamBBlack, tbbRating, tbbRd):
        cmd = 'INSERT INTO ' + self.config.get('Database','table_games') + '('
        for field in self.SCHEMA_GAMES:
             cmd += field[0] + ','
        cmd = cmd[:-1]
        cmd += ') VALUES (\''
        for value in (t, \
                      teamAWhite, tawRating, tawRd, \
                      teamABlack, tabRating, tabRd, \
                      teamBWhite, tbwRating, tbwRd, \
                      teamBBlack, tbbRating, tbbRd):
            cmd += str(value) + '\',\''
        cmd = cmd[:-3]
        cmd += '\');'
        self.c.execute(cmd)
        self.conn.commit()

    #--------------------------------------------------------------------------
    # setup/testing stuff
    #--------------------------------------------------------------------------
    # this should create whatever files or dependencies are necessary for this
    # db implementation to work...
    #
    # for example. DbText creates players.dat and games.dat
    #
    def __init__(self):
        # Read configuration file
        self.config = SafeConfigParser()
        self.config.read('config.ini')

        # Connect to database
        print 'Connecting to database [' + self.config.get('Database','filename') + ']...'
        self.conn = sqlite3.connect(self.config.get('Database','filename'))
        self.c = self.conn.cursor()
