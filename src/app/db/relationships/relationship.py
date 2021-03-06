from db.entity_manager import EntityManager
import logging
class Relationship:
   from_table = ""
   local_key = ""
   foreign_key = ""
   foreign_table = ""
   foreign_entity = None
   local_entity = None
   
   foreign_entity_name = ""
   local_entity_name = ""

   _data = None

   """
   All entity names must be declared in ```/app/entities/__init__.py```
   """
   def __init__(self, local_entity_name, foreign_entity_name, foreign_key = None, local_key = None):
      self.local_entity_name = local_entity_name
      self.foreign_entity_name = foreign_entity_name
      self.foreign_key = foreign_key  if foreign_key else foreign_entity_name + "_id"
      self.local_key = local_key if local_key is not None else foreign_entity_name+"_id"
      self.manager = EntityManager()
      self.db = self.manager.db
      self._data = None

   def get_all_foreign_entities(self):
      self.db.query()

   def boot(self, local_entity, remote_entity):
      self.local_entity = local_entity()
      self.foreign_entity = remote_entity()

      self.from_table = self.local_entity.table_name
      

      self.foreign_table = self.foreign_entity.table_name

   def build(self, data):
      logging.debug("ASSIGNING DATA TO RELATIONSHIP: %s", data)
      self._data = data #data to save in either foreign or local table
      # if self.local_entity.class_name in data:
      #    self._local_data = data[self.local_entity.class_name]
      # if self._foreign_entity.class_name in data:
      #    self._foreign_data = data[self._foreign_entity.class_name]

   def destroy(self, entity):
      pass

   def find(self):
      pass

   def save(self, entity):
      """
      entity: Local entity that is going to be saved
      data to be saved can be accessed in self._data
      """
      pass
   