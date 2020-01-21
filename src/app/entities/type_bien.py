from db.entity import Entity
from db.relationships.one_to_many import OneToMany

class TypeBien(Entity):
   _table_name = "type_bien"
   fields = {
      "type_bien" : "string",
   }
   def render(self):
      pass
   def render_excerpt(self):
      return "({})Location {}".format(self.key, self.name)