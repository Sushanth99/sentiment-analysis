import pymysql.cursors

class ConnectionError(Exception):
	pass

class CredentialsError(Exception):
    pass

class SQLError(Exception):
    pass

class UseDatabase:

	def __init__(self, config: dict) -> None:
		self.configuration = config	

	def __enter__(self) -> 'cursor':
		try:
			self.conn = pymysql.connect(**self.configuration)
			self.cursor = self.conn.cursor()
			return self.cursor	
		except pymysql.InterfaceError as err:
			raise ConnectionError(err)
		except pymysql.ProgrammingError as err:
			raise CredentialsError(err)

	def __exit__(self, exc_type, exc_value, exc_trace) -> None:
		self.conn.commit()
		self.cursor.close()
		self.conn.close()
		if exc_type is pymysql.ProgrammingError:
			raise SQLError(exc_value)
		elif exc_type:
			raise exc_type(exc_value)
