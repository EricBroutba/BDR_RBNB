from db.entity import Entity

class Location(Entity):
   _table_name = "locations"
   fields = {
      "name" : "string"
   }
   def render(self):
      pass
   def render_excerpt(self):
      return "({})Location {}".format(self.key, self.name)