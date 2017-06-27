#Version 3.1

import re
import json #For the example in main()
import sqlite3

#For multi-threading
import sqlalchemy

class Database():
	"""Used to create and interact with a database.
	To expand the functionality of this API, see: "https://www.sqlite.org/lang_select.html"
	"""

	def __init__(self, fileName = None, applyChanges = True, multiThread = False):
		"""Defines internal variables.
		A better way to handle multi-threading is here: http://code.activestate.com/recipes/526618/

		fileName (str) - If not None: Opens the provided database automatically

		Example Input: Database()
		Example Input: Database("emaildb")
		"""

		#Internal variables
		self.defaultFileExtension = ".db"
		self.connection = None
		self.cursor = None
		self.defaultCommit = None

		self.foreignKeys_catalogue = {} #A dictionary of already found foreign keys. {relation: {attribute: [foreign_relation, foreign_attribute]}}

		#Initialization functions
		if (fileName != None):
			self.openDatabase(fileName = fileName , applyChanges = applyChanges, multiThread = multiThread)

	def __del__(self):
		"""Makes sure that the opened database has been closed."""

		if (self.connection != None):
			self.closeDatabase()

	#Utility Functions
	def getType(self, pythonType):
		"""Translates a python data type into an SQL data type.
		These types are: INTEGER, TEXT, BLOB, REAL, and NUMERIC.

		pythonType (type) - The data type to translate

		Example Input: getType(str)
		"""

		sqlType = None
		if (pythonType == str):
			sqlType = "TEXT"

		elif (pythonType == int):
			sqlType = "INTEGER"

		#I am not sure if this is correct
		# elif (pythonType == float):
		# 	sqlType = "REAL"

		else:
			print("Add", pythonType, "to getType()")

		return sqlType

	def getRelationNames(self, exclude = []):
		"""Returns the names of all relations (tables) in the database.

		exclude (list) - A list of which relations to excude from the returned result

		Example Input: getRelationNames()
		Example Input: getRelationNames(["Users", "Names"])
		"""

		exclude.append("sqlite_sequence")

		relationList = self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
		relationList = [relation[0] for relation in relationList if relation[0] not in exclude]

		return relationList

	def getAttributeNames(self, relation, exclude = []):
		"""Returns the names of all attributes (columns) in the given relation (table).

		relation (str) - The name of the relation
		exclude (list) - A list of which attributes to excude from the returned result

		Example Input: getAttributeNames("Users")
		Example Input: getAttributeNames("Users", ["age", "height"])
		"""

		table_info = list(self.cursor.execute("PRAGMA table_info([{}])".format(relation)))
		attributeList = [attribute[1] for attribute in table_info if attribute[1] not in exclude]

		return attributeList

	def updateInternalforeignSchemas(self):
		"""Only remembers data from schema (1) is wanted and (2) that is tied to a foreign key.
		Special Thanks to Davoud Taghawi-Nejad for how to get a list of table names on https://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python-sqlite3-api
		"""

		#Get the table names
		relationList = self.getRelationNames()

		#Get the foreign schema for each relation
		for relation in relationList:
			foreign_schemaList = list(self.cursor.execute("PRAGMA foreign_key_list([{}])".format(relation)))

			#Do not check for relations with no foreign keys in their schema
			if (len(foreign_schemaList) > 0):
				if (relation not in self.foreignKeys_catalogue):
					self.foreignKeys_catalogue[relation] = {}

				#Connect for each foreign key in the schema
				for foreign_schema in foreign_schemaList:
					#Parse schema
					foreign_relation = foreign_schema[2]
					foreign_attribute = foreign_schema[4]
					attribute_connection = foreign_schema[3]

					#Remember this key to speed up future look ups
					self.foreignKeys_catalogue[relation][attribute_connection] = [foreign_relation, foreign_attribute]

	def findForeign(self, relation, attribute):
		"""Determines if and how a key is connected to a foreign table."""

		foreignKey = []

		if (relation in self.foreignKeys_catalogue):
			if (attribute in self.foreignKeys_catalogue[relation]):
				foreignKey = (self.foreignKeys_catalogue[relation][attribute])

		return foreignKey

	#Interaction Functions
	def openDatabase(self, fileName = "myDatabase", applyChanges = True, multiThread = False):
		"""Opens a database.If it does not exist, then one is created.
		Note: If a database is already opened, then that database will first be closed.
		Special thanks toLarry Lustig for help with multi-threading on http://stackoverflow.com/questions/22739590/how-to-share-single-sqlite-connection-in-multi-threaded-python-application
		# Special thanks to culix for help with multi-threading on http://stackoverflow.com/questions/6297404/multi-threaded-use-of-sqlalchemy

		fileName (str)      - The name of the database file
		applyChanges (bool) - Determines the default for when changes are saved to the database
			If True  - Save after every change. Slower, but more reliable because data will be saved in the database even if the program crashes
			If False - Save when the user tells the API to using saveDatabase() or the applyChanges parameter in an individual function. Faster, but data rentention is not ensured upon crashing
		multiThread (bool)  - If True: Will allow mnultiple threads to use the same database

		Example Input: openDatabase("emaildb")
		Example Input: openDatabase("emaildb.sqllite")
		Example Input: openDatabase("emaildb", applyChanges = False)
		Example Input: openDatabase("emaildb", multiThread = True)
		"""

		#Check for another open database
		if (self.connection != None):
			self.closeDatabase()

		#Check for file extension
		if ("." not in fileName):
			fileName += self.defaultFileExtension

		#Configure Options
		self.defaultCommit = applyChanges

		#Establish connection
		if (multiThread):
			#Temporary fix until I learn SQLAlchemy to do this right
			self.connection = sqlite3.connect(fileName, check_same_thread = False)
		else:
			self.connection = sqlite3.connect(fileName)

		self.cursor = self.connection.cursor()

		#Update internal foreign schema catalogue
		self.updateInternalforeignSchemas()

	def closeDatabase(self):
		"""Closes the opened database.

		Example Input: closeDatabase()
		"""

		#Error check
		if (self.connection != None):
			self.cursor.close()

			self.connection = None
			self.cursor = None
		else:
			print("ERROR: No database is open")

	def saveDatabase(self):
		"""Saves the opened database.

		Example Input: saveDatabase()
		"""

		#Save changes
		self.connection.commit()

	def removeRelation(self, relation = None, applyChanges = None):
		"""Removes an entire relation (table) from the database if it exists.
		Special thanks to Jimbo for help with spaces in database names on http://stackoverflow.com/questions/10920671/how-do-you-deal-with-blank-spaces-in-column-names-in-sql-server

		relation (str)      - What the relation is called in the .db
			- If None: All tables will be removed from the .db
		applyChanges (bool) - Determines if the database will be saved after the change is made.
			- If None: The default flag set upon opening the database will be used

		Example Input: removeRelation()
		Example Input: removeRelation("Users")
		"""

		#Error check
		if (self.connection != None):
			if (relation != None):
				#Ensure correct spaces format
				command = "DROP TABLE IF EXISTS [{}]".format(relation)
				self.cursor.execute(command)
			else:
				pass

			#Save Changes
			if (applyChanges == None):
				applyChanges = self.defaultCommit

			if (applyChanges):
				self.saveDatabase()

			#Update internal foreign schema catalogue
			self.updateInternalforeignSchemas()
		else:
			print("ERROR: No database is open")

	def clearRelation(self, relation = None, applyChanges = None):
		"""Removes all rows in the given relation. The relation will still exist.

		relation (str)      - What the relation is called in the .db
			- If None: All relations will be cleared on the .db
		applyChanges (bool) - Determines if the database will be saved after the change is made.
			- If None: The default flag set upon opening the database will be used

		Example Input: clearRelation()
		"""

		#Update internal foreign schema catalogue
		self.updateInternalforeignSchemas()

		#Save Changes
		if (applyChanges == None):
			applyChanges = self.defaultCommit

		if (applyChanges):
			self.saveDatabase()

	def createRelation(self, relation, schema = {}, applyChanges = None, autoPrimary = True, 
		notNull = {}, primary = {}, autoIncrement = {}, unsigned = {}, unique = {}, 
		foreign = None, noReplication = True):
		"""Adds a relation (table) to the database.
		Special thanks to Jimbo for help with spaces in database names on http://stackoverflow.com/questions/10920671/how-do-you-deal-with-blank-spaces-in-column-names-in-sql-server
		
		relation (str)      - What the relation will be called in the .db
		schema (dict)       - The relation schema. {attribute (str): data type (type)}
			If a dictionary with multiple elements is given, the order will be randomized
			If a list of one element dictionaries is given, the order will be the order of the list
		applyChanges (bool) - Determines if the database will be saved after the change is made
			- If None: The default flag set upon opening the database will be used
		autoPrimary (bool)   - Determines if a primary key will automatically be added to the new table. If notNull, primary, autoIncrement, or unsigned are given, they will override the defaults for this option

		notNull (dict)       - Determines how the initial value is assigned to a given attribute. {attribute (str): flag (bool)}
			- If True: Signals to the database that this will be used a lot
		primary (dict)       - Tells the database that this is the primary key (the relation id). {attribute (str): flag (bool)}
		autoIncrement (dict) - Determines if the attribute's value will increment every time it is written to. {attribute (str): flag (bool)}
		unsigned (dict)      - Determines if the attribute's value will be able to be negative. {attribute (str): flag (bool)}
		unique (dict)        - Signals to the database that there cannot be more than one attribute with this name
		
		foreign (str)        - If not None: Tells the database that this is the foreign key (a link to another relation). Can be a list if more than one foreign key is given. {attribute (str): foreign relation (str)}
		noReplication (bool) - If True: The table will not be created if it does not already exist
			- If None: Will delete the previously existing table if it exists

		Example Input: createRelation("Users", {"email": str, "count": int})
		Example Input: createRelation("Users", [{"email": str}, {"count": int}])
		Example Input: createRelation("Users", {"email": str, "count": int}, applyChanges = False)
		Example Input: createRelation("Users", {"id": int, "email": str, "count": int}, notNull = {"id": True}, primary = {"id": True}, autoIncrement = {"id": True}, unique = {"id": True}, autoPrimary = False)
		
		Example Input: createRelation("Names", [{"first_name": str}, {"extra_data": str}], unique = {"first_name": True})
		Example Input: createRelation("Users", {"age": int, "height": int}, foreign = {"name": {"Names": "first_name"}})
		Example Input: createRelation("Users", {"age": int, "height": int}, foreign = {"name": {"Names": "first_name"}, "address": {"Address": "street"}})
		"""

		def formatSchema(schemaFormatted, item, autoPrimary_override):
			"""A sub-function that formats the schema for the user."""

			if ((len(notNull) != 0) or (autoPrimary_override)):
				if (item in notNull):
					if (notNull[item]):
						schemaFormatted += " NOT NULL"
				elif(autoPrimary_override):
					schemaFormatted += " NOT NULL"

			if ((len(primary) != 0) or (autoPrimary_override)):
				if (item in primary):
					if (primary[item]):
						schemaFormatted += " PRIMARY KEY"
				elif(autoPrimary_override):
					schemaFormatted += " PRIMARY KEY"
				
			if ((len(autoIncrement) != 0) or (autoPrimary_override)):
				if (item in autoIncrement):
					if (autoIncrement[item]):
						schemaFormatted += " AUTOINCREMENT"
				elif(autoPrimary_override):
					schemaFormatted += " AUTOINCREMENT"
				
			# if (len(unsigned) != 0):
				# if (item in unsigned):
				# 	if (unsigned[item]):
				# 		schemaFormatted += " UNSIGNED"
				# elif(autoPrimary_override):
				# 	schemaFormatted += " UNSIGNED"
				
			if ((len(unique) != 0) or (autoPrimary_override)):
				if (item in unique):
					if (unique[item]):
						schemaFormatted += " UNIQUE"
				elif(autoPrimary_override):
					schemaFormatted += " UNIQUE"

			return schemaFormatted

		def addforeign(schemaFormatted, foreignList):
			"""A sub-function that adds a foreign key for the user.
			More information at: http://www.sqlitetutorial.net/sqlite-foreign-key/
			"""

			#Parse foreign keys
			# schema_foreign = {} #
			# print("@1", foreignList)
			for foreign in foreignList:
				for attribute, foreign_dict in foreign.items():
					foreign_relation, foreign_attribute = list(foreign_dict.items())[0]
					# print("@2", attribute, foreign_relation, foreign_attribute)

					#Add the foreign key to the table
					schemaFormatted += "[{}] INTEGER".format(attribute)
					schemaFormatted = formatSchema(schemaFormatted, attribute, False)

					#Account for multiple attributes
					if (schemaFormatted != ""):
						schemaFormatted += ", "

					# print("@7", command + "({})".format(schemaFormatted))

			#Link foreign keys
			for i, foreign in enumerate(foreignList):
				for attribute, foreign_dict in foreign.items():
					foreign_relation, foreign_attribute = list(foreign_dict.items())[0]

					schemaFormatted += "FOREIGN KEY ([{}]) REFERENCES [{}]([{}])".format(attribute, foreign_relation, foreign_attribute)

					#Account for multiple attributes
					if (schemaFormatted != ""):
						schemaFormatted += ", "

					# print("@8", command + "({})".format(schemaFormatted))

			#Remove trailing comma
			schemaFormatted = schemaFormatted[:-2]

			return schemaFormatted

		#Error check
		if (self.connection != None):

			#Build SQL command
			command = "CREATE TABLE "

			if (noReplication != None):
				command += "IF NOT EXISTS "

			else:
				self.removeRelation(relation)

			command += "[" + str(relation) + "]"

			#Ensure correct format
			if (type(schema) != list):
				schemaList = [schema]
			else:
				schemaList = schema

			#Format schema
			firstRun = True
			schemaFormatted = ""

			#Add primary key
			if (len(primary) != 0):
				#Insert rows for foreign keys
				for i, item in enumerate(primary):
					for primaryKey, primaryValue in item.items():
						schemaFormatted += "[{}_id] INTEGER".format(primaryKey.lower())
						schemaFormatted = formatSchema(schemaFormatted, primaryKey, False)

						if (i != len(primary) - 1):
							schemaFormatted += ", "

			elif (autoPrimary):
				schemaFormatted += "id INTEGER"
				schemaFormatted = formatSchema(schemaFormatted, "id", autoPrimary)

			# print("@5", command + "({})".format(schemaFormatted))
			#Add given attributes
			for schema in schemaList:
				for i, item in enumerate(schema.items()):
					if (schemaFormatted != ""):
						schemaFormatted += ", "

					attribute, dataType = item
					schemaFormatted += "[{}] {}".format(attribute, self.getType(dataType))
				
					schemaFormatted = formatSchema(schemaFormatted, attribute, False)

					# print("@6", command + "({})".format(schemaFormatted))

			#Add foreign keys
			if (foreign != None):
				#Ensure correct format
				if ((type(foreign) != list) and (type(foreign) != tuple)):
					foreignList = [foreign]
				else:
					foreignList = foreign

				#Account for primary key
				if (schemaFormatted != ""):
					schemaFormatted += ", "

				schemaFormatted = addforeign(schemaFormatted, foreignList)

			#Execute SQL
			# print("@0", command + "({})".format(schemaFormatted))
			self.cursor.execute(command + "({})".format(schemaFormatted))

			#Save Changes
			if (applyChanges == None):
				applyChanges = self.defaultCommit

			if (applyChanges):
				self.saveDatabase()

			#Update internal foreign schema catalogue
			self.updateInternalforeignSchemas()

		else:
			print("ERROR: No database is open")

	def addTuple(self, relation, myTuple = {}, applyChanges = None, autoPrimary = False, notNull = False, 
		primary = False, autoIncrement = False, unsigned = True, unique = False, checkForeigen = True):
		"""Adds a tuple to the given relation.
		Special thanks to DSM for how to check if a key exists in a list of dictionaries on http://stackoverflow.com/questions/14790980/how-can-i-check-if-key-exists-in-list-of-dicts-in-python
		Special thanks to Jimbo for help with spaces in database names on http://stackoverflow.com/questions/10920671/how-do-you-deal-with-blank-spaces-in-column-names-in-sql-server

		relation (str)      - What the relation is called in the .db
		myTuple (dict)      - What will be written to the tuple. {attribute: value}
		applyChanges (bool) - Determines if the database will be saved after the change is made
			- If None: The default flag set upon opening the database will be used
		autoPrimary (bool)   - Determines if this is a primary key. Will use the primary key defaults. If notNull, primary, autoIncrement, or unsigned are given, they will override the defaults for this option

		notNull (bool)       - Determines how the initial value is assigned to the attribute
			- If True: Signals to the database that this will be used a lot
		primary (bool)       - Tells the database that this is the primary key (the relation id)
		autoIncrement (bool) - Determines if the attribute's value will increment every time it is written to
		unsigned (bool)      - Determines if the attribute's value will be able to be negative
		unique (bool)        - Determines how a unique attribute's value is handled in the case that it already exists in the relation.
			- If True:  Will replace the value of the attribute 
			- If False: Will not account for the value being a unique attribute
			- If None:  Will only insert if that value for the attribute does not yet exist
		checkForeigen (bool) - Determines if foreign keys will be take in account

		Example Input: addTuple("Lorem", autoPrimary = True)
		Example Input: addTuple("Lorem", {"Ipsum": "Dolor", "Sit": 5})
		Example Input: addTuple("Lorem", {"Ipsum": "Dolor", "Sit": 5}, unique = None)
		"""

		def configureForeign(self, command, valueList, relation, attribute, value):
			"""Allows the user to use foreign keys."""

			#Look for foreign keys
			foreign_results = self.findForeign(relation, attribute)

			if (len(foreign_results) != 0):
				foreign_relation, foreign_attribute = foreign_results

				#Add new line to the foreign key
				##Build SQL command
				foreign_command = "INSERT OR IGNORE INTO [{}] ({}) VALUES (?)".format(foreign_relation, foreign_attribute)

				##Run SQL command
				# print("@2", foreign_command, value)
				self.cursor.execute(foreign_command, (value, ))
				# self.saveDatabase()

				#Get the new foreign tuple's id
				foreign_tuple_id = self.getValue({foreign_relation: "id"}, {foreign_attribute: value}, filterRelation = True)
				foreign_tuple_id = foreign_tuple_id["id"][0]

				#Put the foreign id in for tuple in instead of the value
				valueList.append(foreign_tuple_id)


			else:
				#No foreign key found
				valueList.append(value)

			return valueList

		##Build SQL command
		command = "INSERT "

		if (unique != None):
			if (unique):
				command += "OR REPLACE "
		else:
			command += "OR IGNORE "

		command += "INTO [{}] (".format(relation)

		#Build attribute side
		itemList = myTuple.items()
		valueList = []
		for i, item in enumerate(itemList):
			attribute, value = item

			#Remember the associated value for the attribute
			if (checkForeigen):
				valueList = configureForeign(self, command, valueList, relation, attribute, value)
			else:
				valueList.append(value)
			command += attribute

			#Account for multiple items
			if (i != len(itemList) - 1):
				command += ", "

		#Build value side
		command += ") VALUES ("
		for i, value in enumerate(valueList):
			command += "?"

			#Account for multiple items
			if (i != len(itemList) - 1):
				command += ", "

		command += ")"

		##Run SQL command
		# print("@2", command, valueList)
		self.cursor.execute(command, valueList)

		#Save Changes
		if (applyChanges == None):
			applyChanges = self.defaultCommit

		if (applyChanges):
			self.saveDatabase()

	def changeTuple(self, myTuple, nextTo, value, forceMatch = None, defaultValues = {}, applyChanges = None, checkForeigen = True):
		"""Changes a tuple for a given relation.
		Note: If multiple entries match the criteria, then all of those tuples will be chanegd.
		Special thanks to Jimbo for help with spaces in database names on http://stackoverflow.com/questions/10920671/how-do-you-deal-with-blank-spaces-in-column-names-in-sql-server

		myTuple (dict)   - What will be written to the tuple. {relation: attribute to change}
		nextTo (dict)    - An attribute-value pair that is in the same tuple. {attribute next to one to change: value of this attribute}
			- If more than one attribute is given, it will look for all cases
		value (any)      - What will be written to the tuple
		forceMatch (any) - Determines what will happen in the case where 'nextTo' is not found
			- If None: Do nothing
			- If not None: Create a new row that contains the default values

		defaultValues (dict) - A catalogue of what defaults to give attributes. If no default is found, the attribute's value will be None
		applyChanges (bool)  - Determines if the database will be saved after the change is made
			- If None: The default flag set upon opening the database will be used
		checkForeigen (bool) - Determines if foreign keys will be take in account

		Example Input: changeTuple({"Users": "name"}, {"age": 26}, "Amet")
		"""

		def configureForeign(self, valueList, relation, attribute, value):
			"""Allows the user to use foreign keys."""

			#Look for foreign keys
			foreign_results = self.findForeign(relation, attribute)

			if (len(foreign_results) != 0):
				foreign_relation, foreign_attribute = foreign_results

				#Add new line to the foreign key
				##Build SQL command
				foreign_command = "INSERT OR IGNORE INTO [{}] ({}) VALUES (?)".format(foreign_relation, foreign_attribute)

				##Run SQL command
				# print("@2", foreign_command, value)
				self.cursor.execute(foreign_command, (value, ))
				# self.saveDatabase()

				#Get the new foreign tuple's id
				foreign_tuple_id = self.getValue({foreign_relation: "id"}, {foreign_attribute: value}, filterRelation = True)
				if (len(foreign_tuple_id["id"]) == 0):
					print(foreign_tuple_id)
				foreign_tuple_id = foreign_tuple_id["id"][0]

				#Put the foreign id in for tuple in instead of the value
				value = foreign_tuple_id

			else:
				#No foreign key found
				value = value

			return value

		def configureMatching(attribute, relation, criteriaAttribute, criteriaValue, value, checkForeigen):
			"""Allows the user to control what happens if no match is found."""

			#Remember the associated value for the attribute
			valueList = []
			if (checkForeigen):
				value = configureForeign(self, valueList, relation, attribute, value)

			if (forceMatch != None):
				#Select where match should be
				command = "SELECT [{}] FROM [{}] WHERE [{}] = ?".format(attribute, relation, criteriaAttribute)
				# print("@3", command, criteriaValue)
				self.cursor.execute(command, (criteriaValue, ))
				row = self.cursor.fetchone()

				#Check if that spot exits
				if (row is None):
					#Match found
					defaultValues[attribute] = value
					defaultValues[criteriaAttribute] = criteriaValue
					self.addTuple(relation, defaultValues, applyChanges = False)
					return

			#No match found
			command = "UPDATE [{}] SET [{}] = ? WHERE [{}] = ?".format(relation, attribute, criteriaAttribute)
			# print("@2", command, (value, criteriaValue))
			self.cursor.execute(command, (value, criteriaValue))

		#Error check
		if (self.connection != None):
			#Account for multiple tuples to change
			for relation, attribute in myTuple.items():
				#Account for multiple places to look
				for criteriaAttribute, criteriaValue in nextTo.items():
					criteriaAttribute, criteriaValue = str(criteriaAttribute), str(criteriaValue)

					#Configure options
					configureMatching(attribute, relation, criteriaAttribute, criteriaValue, value, checkForeigen)
					
					#Save Changes
					if (applyChanges == None):
						applyChanges = self.defaultCommit

					if (applyChanges):
						self.saveDatabase()

		else:
			print("ERROR: No database is open")

	def getAllValues(self, relation, exclude = [], orderBy = None, limit = None, direction = None, nextToCondition = True, 
		checkForeigen = True, filterTuple = True, filterRelation = True, filterForeign = None, valuesAsList = False):
		"""Returns all values in the given relation (table) that match the filter conditions.

		relation (str) - Which relation to look in
			- If a list is given, it will look in each table. 
		exclude (list) - A list of which tables to excude from the returned result
			- If multiple tables are required, provide a dictionary for the tabel elements. {table 1: [attribute 1, attribute 2], table 2: attribute 3}
			- If a list or single value is given, it will apply to all tables given

		Example Input: getAllValues("Users")
		Example Input: getAllValues("Users", ["age"])
		
		Example Input: getAllValues(["Users"])
		Example Input: getAllValues(["Users", "Names"])
		Example Input: getAllValues(["Users", "Names"], {"Users": "age"})
		Example Input: getAllValues(["Users", "Names"], {"Users": ["age", "height"]})
		Example Input: getAllValues(["Users", "Names"], {"Users": ["age", "height"], "Names": "extra_data"})
		Example Input: getAllValues(["Users", "Names"], "id")
		"""

		#Ensure correct format
		if ((type(relation) != list) and (type(relation) != tuple)):
			relationList = [relation]
		else:
			relationList = relation

		myTuple = {}
		for relation in relationList:
			#Ensure correct format
			if (type(exclude) == dict):
				if (relation in exclude):
					excludeList = exclude[relation]
				else:
					excludeList = []
			
			if ((type(exclude) != list) and (type(exclude) != tuple)):
				excludeList = [exclude]
			else:
				excludeList = exclude[:]

			#Build getValue query
			attributeNames = self.getAttributeNames(relation, excludeList)
			myTuple[relation] = attributeNames

		# print("@5", myTuple)
		results_catalogue = self.getValue(myTuple, orderBy = orderBy, limit = limit, direction = direction, nextToCondition = nextToCondition, 
			checkForeigen = checkForeigen, filterTuple = filterTuple, filterRelation = filterRelation, filterForeign = filterForeign, valuesAsList = valuesAsList)

		return results_catalogue

	def getValue(self, myTuple, nextTo = None, orderBy = None, limit = None, direction = None, nextToCondition = True, 
		checkForeigen = True, filterTuple = True, filterRelation = True, filterForeign = None, valuesAsList = False):
		"""Gets the value of an attribute in a tuple for a given relation.
		If multiple attributes match the criteria, then all of the values will be returned.
		If you order the list and limit it; you can get things such as the 'top ten occurrences', etc.

		myTuple (dict)   - What to return. {relation: attribute}. A list of attributes can be returned. {relation: [attribute 1, attribute 2]}
			- If an attribute is a foreign key: {relation: {foreign relation: foreign attribute}}
		nextTo (dict)    - An attribute-value pair that is in the same tuple. {attribute: value}
			- If multiple keys are given, one will be 'chosen at random'
			- If an attribute is a foreign key: {value: {foreign relation: foreign attribute}}
		orderBy (any)    - Determines whether to order the returned values or not. A list can be given to establish priority for multiple things
			- If None: Do not order
			- If not None: Order the values by the given attribute
		limit (int)      - Determines whether to limit the number of values returned or not
			- If None: Do not limit the return results
			- If not None: Limit the return results to this many
		direction (bool) - Determines if a descending or ascending condition should be appled. Used for integers. If a list is given for 'orderBy', either
			(A) a list must be given with the same number of indicies, (B) a single bool given that will apply to all, or (C) a dictionary given where the 
			key is the item to adjust and the value is the bool for that item
			- If True: Ascending order
			- If False: Descending order
			- If None: No action taken

		nextToCondition (bool) - Determines how to handle multiple nextTo criteria
			- If True: All of the criteria given must match
			- If False: Any of the criteria given must match
		checkForeigen (bool)   - Determines if foreign keys will be take in account
		filterTuple (bool)     - Determines how the final result in the catalogue will be returned if there is only one column
			- If True: (value 1, value 2, value 3...)
			- If False: ((value 1, ), (value 2, ), (value 3. ),..)
		filterRelation (bool)  - Determines how catalogue will be returned
			- If True: {attribute 1: values, attribute 2: values}
				For multiple relations: {attribute 1 for relation 1: values, attribute 2 for relation 1: values, attribute 1 for relation 2: values}
			- If False: {relation: {attribute 1: values, attribute 2: values}}
				For multiple relations: {relation 1: {attribute 1 for relation 1: values, attribute 2 for relation 1: values}, {attribute 1 for relation 2: values}}
		filterForeign (bool)   - Determines how results of foreign attributes will be returned
			- If True: Returns only the values that have valid foreign keys
			- If False: Returns all values and replaces values that have valid foreign keys
			- If None:  Returns Replaces values that have valid foreign keys and fills in a None for values with invalid foreign keys
		valuesAsList (bool)    - Determines if the values returned should be a list or a tuple
			- If True: Returned values will be in a list
			- If False: Returned values will be in a tuple

		Example Input: getValue({"Users": "name"})
		Example Input: getValue({"Users": "name"}, valuesAsList = True)
		Example Input: getValue({"Users": "name"}, filterRelation = False)
		Example Input: getValue({"Users": ["name", "age"]})

		Example Input: getValue({"Users": "name"}, orderBy = "age")
		Example Input: getValue({"Users": ["name", "age"]}, orderBy = "age", limit = 2)
		Example Input: getValue({"Users": ["name", "age"]}, orderBy = "age", direction = True)

		Example Input: getValue({"Users": ["name", "age"]}, orderBy = ["age", "height"])
		Example Input: getValue({"Users": ["name", "age"]}, orderBy = ["age", "height"], direction = [None, False])
		Example Input: getValue({"Users": ["name", "age"]}, orderBy = ["age", "height"], direction = {"height": False})

		Example Input: getValue({"Users": "name", "Names": "first_name"})
		Example Input: getValue({"Users": "name", "Names": "first_name"}, filterRelation = False)
		Example Input: getValue({"Users": "name", "Names": ["first_name", "extra_data"]})

		Example Input: getValue({"Users": "name"}, filterTuple = False)
		Example Input: getValue({"Users": "name"}, filterForeign = True)
		Example Input: getValue({"Users": "name"}, filterForeign = False)

		Example Input: getValue({"Users": "name"}, {"age": 24})
		Example Input: getValue({"Users": "name"}, {"age": 24, height: 6})
		Example Input: getValue({"Users": "name"}, {"age": 24, height: 6}, nextToCondition = False)

		Example Input: getValue({"Users": "age"}, {"name": "John"})
		Example Input: getValue({"Users": "age"}, {"name": ["John", "Jane"]})
		"""

		def configureSelection(self, relation, attribute):
			"""Allows the user to choose what attribute to search for."""

			#Ensure correct format
			if ((type(attribute) != list) or (type(attribute) != tuple)):
				attribute = [attribute]

			##Build SQL command
			command = "SELECT "

			#Account for multiple attributes
			for i, item in enumerate(attribute):
				command += "[{}].[{}]".format(relation, item) 

				#Account for the last element not having a comma
				if (i < len(attribute) - 1):
					command += ", "

			# print("@1", command)
			return command

		def configureSource(self, command, relation):
			"""Allows the user to choose the relation to search for the attribute in."""

			##Build SQL command
			command += " FROM [" + str(relation) + "]"

			# print("@2", command)

			return command

		def configureOrder(self, command, orderBy, direction):
			"""Allows the user to change the order in which the result is returned."""
			def configureDirection(self, command, direction):
				"""Sets up the SQL command for the correct direction"""

				#Configure display direction
				if (type(direction) != dict):
					if (len(direction) == 1):
						if (direction[0] != None):
							if (direction[0]):
								command += " ASC"
							else:
								command += " DESC"
					else:
						if (direction[i] != None):
							if (direction[i]):
								command += " ASC"
							else:
								command += " DESC"
				else:
					condition = direction.get(item, None)						
					if (condition != None):
						if (condition):
							command += " ASC"
						else:
							command += " DESC"

				return command

			if (orderBy != None):
				##Build SQL
				command += " ORDER BY "

				#Ensure correct format
				if ((type(orderBy) != list) and (type(orderBy) != tuple)):
					orderBy = [orderBy]
				if ((type(direction) != list) and (type(direction) != tuple) and (type(direction) != dict)):
					direction = [direction]

				#Error checking
				if (type(direction) != dict):
					if (len(direction) != 1):
						if (len(direction) != len(orderBy)):
							print("ERROR: 'orderBy' and 'direction' size do not match.")
							return

				#Account for multiple conditions
				for i, item in enumerate(orderBy):
					##Build SQL
					command += "[{}]".format(item)

					command = configureDirection(self, command, direction)

					#Account for the last element not having a ','
					if (i < len(orderBy) - 1):
						command += ", "

			return command

		def configureLimit(self, command, limit):
			"""Allows the user to limit how many results are returned."""

			##Number of items displayed
			if (limit != None):
				command += " LIMIT {}".format(limit)

			return command

		def configureForeign_command(self, relation, attributeList, checkForeigen):
			"""Allows the user to use foreign keys.
			For more information on JOIN: https://www.techonthenet.com/sqlite/joins.php
			"""

			commandSegment = ""
			if (checkForeigen):
				#Ensure correct format
				if ((type(attributeList) != list) and (type(attributeList) != tuple)):
					attributeList = [attributeList]

				#Account for multiple attributes
				for attribute in attributeList:
					#Look for foreign keys
					foreign_results = self.findForeign(relation, attribute)
					# print("@2", foreign_results, relation, attribute)

					if (len(foreign_results) != 0):
						foreign_relation, foreign_attribute = foreign_results
									
						#Build on the command
						#Choose how to filter results
						if (filterForeign == True):
							foreign_method = "INNER"
						else:
							foreign_method = "LEFT OUTER"

						#Building the command string
						commandSegment += " {} JOIN [{}] ON [{}].[{}] = [{}].[id]".format(foreign_method, foreign_relation, relation, attribute, foreign_relation)

			return commandSegment

		def configureForeign_results(self, results, relation, attribute, checkForeigen, filterTuple, filterForeign, valuesAsList):
			"""Allows the user to use foreign keys.
			For more information on JOIN: https://www.techonthenet.com/sqlite/joins.php
			"""

			valueList = []
			if (checkForeigen):
				foreign_results = self.findForeign(relation, attribute)

				if (len(foreign_results) != 0):
					foreign_relation, foreign_attribute = foreign_results

					#Account for multiple results
					for item in results:
						#Skip empty cells
						if (item != None):
							#Modifying the results catalogue
							# print("@5", results, item, relation, attribute, foreign_attribute)
							foreign_command = "SELECT [{}].[{}] FROM [{}] WHERE [id] = ?".format(foreign_relation, foreign_attribute, foreign_relation)

							#Format results
							if (filterTuple):
								# print("@8", foreign_command, item)
								result = self.cursor.execute(foreign_command, (item, ))
								result = tuple(result)

								#Account for value not existing
								if (len(result[0][0]) != 0):
									result = result[0][0]
								else:
									if (filterForeign != None):
										if (filterForeign):
											result = []
										else:
											result = item
									else:
										result = None

							else:
								result = self.cursor.execute(foreign_command, (item[0], ))
								result = tuple(result)

								#Account for value not existing
								if (len(result[0]) != 0):
									result = result[0]
								else:
									if (filterForeign != None):
										if (filterForeign):
											result = []
										else:
											result = item
									else:
										result = None

						else:
							result = None

						if (result != None):
							if (len(result) != 0):
								valueList.append(result)
						else:
							valueList.append(result)


			if (valuesAsList):
				valueList = list(valueList)
			else:
				valueList = tuple(valueList)

			return valueList

		def configureForeign_location(self, i, relation, attribute, checkForeigen):
			"""Allows the user to use foreign keys with the 'next to' filter."""

			location = ""
			if (checkForeigen):
				foreign_results = self.findForeign(relation, attribute)

				#Account for no foreign keys found
				if (len(foreign_results) != 0):
					foreign_relation, foreign_attribute = foreign_results

					#Account for 'next to' filter
					location += "[{}].[{}] = ?".format(foreign_relation, foreign_attribute)
					
					##Account for multiple references
					if (i != 0):
						location += " OR "
				else:
					location += "[{}].[{}] = ?".format(relation, attribute)

			return location

		def runSQL(self, command, nextTo, filterTuple, relation, attribute, valuesAsList):
			"""Runs the SQL command."""

			if (nextTo != None):
				#Ensure correct format
				if ((type(nextTo) == list) or (type(nextTo) == tuple)):
					print("A", type(nextTo), "cannot be given for nextTo")
					return None

				#Setup conditions
				valueList = [] #Where the values to replace the '?'s are stored
				locationInfo = "" #Where the filter code is stored
				foreign_commandSegmentList = [] #Where the foreign keys are stored
				itemList = list(nextTo.items()) #The keys and values to look for the target next to
				
				commandSegment = configureForeign_command(self, relation, attribute, checkForeigen)
				# print("@6", commandSegment, relation, attribute)

				if ((commandSegment != "") and (commandSegment not in foreign_commandSegmentList)):
					foreign_commandSegmentList.append(commandSegment)

				for i, item in enumerate(itemList):
					key, value = item
					valueList.append(value)

					#Account for foreign keys
					if (key != attribute):
						commandSegment = configureForeign_command(self, relation, key, checkForeigen)
						foreign_commandSegmentList.append(commandSegment)

					locationInfo = configureForeign_location(self, i, relation, key, checkForeigen)
					# print("@3", locationInfo)

				#Account for foreign keys
				for commandSegment in foreign_commandSegmentList:
					command += "{} ".format(commandSegment)

				#Account for 'next to' filter
				if (len(locationInfo) != 0):
					command += "WHERE ({})".format(locationInfo)

				##Run SQL command
				# print("@4", command, valueList)
				results = self.cursor.execute(command, tuple(valueList))
			else:

				##Run SQL command
				# print("@5", command)
				results = self.cursor.execute(command)

			#Format results
			if (filterTuple):
				results = list(results)
				if (len(results) > 0):
					if (len(results[0]) == 1):
						for i, item in enumerate(results):
							results[i] = item[0]
			
			if (valuesAsList):
				results = list(results)
			else:
				results = tuple(results)
			return results

		def catalogueResults(self, results, relation, attribute, checkForeigen, filterTuple, filterForeign, valuesAsList):
			"""Allows the user to recieve a dictionary of all requested values."""
			
			#Account for foreign keys
			configuredResults = configureForeign_results(self, results, relation, attribute, checkForeigen, filterTuple, filterForeign, valuesAsList)

			#Account for no foreign keys
			if (len(configuredResults) != 0):
				results = configuredResults

			#Add results to catalogue
			if (filterRelation):
				results_catalogue[attribute] = results
			else:
				if (relation not in results_catalogue):
					results_catalogue[relation] = {}

				results_catalogue[relation][attribute] = results
			return results_catalogue

		#Error check
		if (self.connection != None):
			itemList = myTuple.items()

			results_catalogue = {}
			for i, item in enumerate(itemList):
				relation, attributeList = item

				#Ensure correct format
				if ((type(attributeList) != list) and (type(attributeList) != tuple)):
					attributeList = [attributeList]

				#Account for multiple items
				for attribute in attributeList:
					#Select Items
					command = configureSelection(self, relation, attribute)
					command = configureSource(self, command, relation)
					
					#Add final options
					command = configureOrder(self, command, orderBy, direction)
					command = configureLimit(self, command, limit)
					
					#Finish
					results = runSQL(self, command, nextTo, filterTuple, relation, attribute, valuesAsList)
					results_catalogue = catalogueResults(self, results, relation, attribute, checkForeigen, filterTuple, filterForeign, valuesAsList)


			# print("@2", results_catalogue)
			return results_catalogue

		else:
			print("ERROR: No database is open")
			return None

	#User-friendly functions	
	def removeTable(self, table = None, applyChanges = None):
		"""User-friendly function for removeRelation()."""

		self.removeRelation(relation = table, applyChanges = applyChanges)

	def clearTable(self, table = None, applyChanges = None):
		"""User-friendly function for clearRelation()."""

		self.clearRelation(relation = table, applyChanges = applyChanges)

	def createTable(self, name, contract = {}, applyChanges = None, autoPrimary = True, notNull = {}, 
		primary = {}, autoIncrement = {}, unsigned = {}, unique = {}, foreign = None, noReplication = True):
		"""User-friendly function for createRelation()."""

		self.createRelation(name, schema = contract, applyChanges = applyChanges, autoPrimary = autoPrimary, notNull = notNull, 
			primary = primary, autoIncrement = autoIncrement, unsigned = unsigned, unique = unique, foreign = foreign, noReplication = noReplication)

	def addRow(self, table, addThis, applyChanges = None, autoPrimary = False, notNull = False, 
		primary = False, autoIncrement = False, unsigned = True, unique = False, checkForeigen = True):
		"""User-friendly function for addTuple()."""

		self.addTuple(table, addThis, applyChanges = applyChanges, autoPrimary = autoPrimary, notNull = notNull, 
		primary = primary, autoIncrement = autoIncrement, unsigned = unsigned, unique = unique, checkForeigen = checkForeigen)

	def changeCell(self, changeThis, nextToThis, toThis, forceMatch = None, defaultValues = {}, applyChanges = None):
		"""User-friendly function for changeTuple()."""

		self.changeTuple(changeThis, nextToThis, toThis, forceMatch = forceMatch, defaultValues = defaultValues, applyChanges = applyChanges)

	def getTableNames(self, exclude = []):
		"""User-friendly function for getRelationNames()."""

		tableNames = self.getRelationNames(exclude = exclude)
		return tableNames

	def getColumnNames(self, table, exclude = []):
		"""User-friendly function for getAttributeNames()."""

		columnNames = self.getAttributeNames(table, exclude = exclude)
		return columnNames

def main():
	"""The main program controller."""

	#Create the database
	database_API = Database()
	database_API.openDatabase("test.db", applyChanges = False)
	database_API.removeTable("Users")
	database_API.removeTable("Names")
	database_API.removeTable("Address")

	#Create tables from the bottom up
	database_API.createTable("Names", [{"first_name": str}, {"extra_data": str}], unique = {"first_name": True})
	database_API.createTable("Address", {"street": str}, unique = {"street": True})
	database_API.saveDatabase()
	database_API.createTable("Users", {"age": int, "height": int}, foreign = {"name": {"Names": "first_name"}, "address": {"Address": "street"}})

	database_API.addRow("Names", {"first_name": "Dolor", "extra_data": "Sit"}, unique = None)
	
	database_API.addRow("Users", {"name": "Ipsum", "age": 26, "height": 5}, unique = None)
	database_API.addRow("Users", {"name": "Lorem", "age": 26, "height": 6}, unique = None)
	database_API.addRow("Users", {"name": "Lorem", "age": 24, "height": 3}, unique = None)
	database_API.addRow("Users", {"name": "Dolor", "age": 21, "height": 4}, unique = None)
	database_API.addRow("Users", {"name": "Sit", "age": None, "height": 1}, unique = None)

	# # Simple actions
	# print(database_API.getValue({"Users": "name"}))
	# print(database_API.getValue({"Users": "name"}, filterRelation = False))
	# print(database_API.getValue({"Users": ["name", "age"]}))

	# #Ordering data
	# print(database_API.getValue({"Users": "name"}, orderBy = "age"))
	# print(database_API.getValue({"Users": ["name", "age"]}, orderBy = "age", limit = 2))
	# print(database_API.getValue({"Users": ["name", "age"]}, orderBy = "age", direction = True))

	# print(database_API.getValue({"Users": ["name", "age"]}, orderBy = ["age", "height"]))
	# print(database_API.getValue({"Users": ["name", "age"]}, orderBy = ["age", "height"], direction = [None, False]))
	# print(database_API.getValue({"Users": ["name", "age"]}, orderBy = ["age", "height"], direction = {"height": False}))

	# #Multiple Relations
	# print(database_API.getValue({"Users": "name", "Names": "first_name"}))
	# print(database_API.getValue({"Users": "name", "Names": "first_name"}, filterRelation = False))
	# print(database_API.getValue({"Users": "name", "Names": ["first_name", "extra_data"]}))

	# #Changing attributes
	# print(database_API.getValue({"Users": "name"}))
	# database_API.changeCell({"Names": "first_name"}, {"first_name": "Lorem"}, "Amet")
	# print(database_API.getValue({"Users": "name"}))
	# print(database_API.getValue({"Users": "name"}, filterForeign = True))

	# database_API.changeCell({"Users": "name"}, {"age": 26}, "Consectetur", forceMatch = True)
	print(database_API.getValue({"Users": "name"}))
	print(database_API.getValue({"Users": "name"}, valuesAsList = True))
	# print(database_API.getValue({"Users": "name"}, filterForeign = True))
	# print(database_API.getValue({"Users": "name"}, filterForeign = False))

	# database_API.changeCell({"Users": "name"}, {"age": 26}, "Amet")

	database_API.saveDatabase()
if __name__ == '__main__':
	main()
	pass