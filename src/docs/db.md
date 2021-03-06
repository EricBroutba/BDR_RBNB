
# One to many relationship

TO define a one to many relationship you need to define a relationship in your base model and add the foreign key field in the fields of the remote entity.

```
OneToMany(base_table, foreign_table, foreign_key, local_key)
```



Example

__```User```:__

```
from db.entity import Entity
from .location import Location
from db.relationships.one_to_many import OneToMany

class User(Entity):
   _table_name = "users"
   
   fields = {
      "name": "string",
   }
   relationships = {
      "locations" : OneToMany("user", "location", "user_id")
   }
```

And on your remote model ```Location```
__```Location```:__
```
from db.entity import Entity
from db.relationships.one_to_one import OneToOne

class Location(Entity):
   _table_name = "locations"
   fields = {
      "name" : "string",
      "user_id" : "relationship"
   }
   

```

Then you can use the class as follow

```

User.create({
   'username': 'test',
})

user.locations = Location.find()

user.save()
```


# One to One

One to one relationships are either a relationship in itself or the opposite of a one to many relationship

```
OneToOne(base_table, foreign_table, foreign_key, local_key)
```

Example


__```User```:__

```
from db.entity import Entity
from .location import Location
from db.relationships.one_to_many import OneToMany

class User(Entity):
   _table_name = "users"
   
   fields = {
      "name": "string",
   }
   relationships = {
      "locations" : OneToMany("user", "location", "user_id")
   }
```

And on your remote model ```Location```

__```Location```:__
```
from db.entity import Entity
from db.relationships.one_to_one import OneToOne

class Location(Entity):
   _table_name = "locations"
   fields = {
      "name" : "string",
      "user_id" : "relationship"
   }
   relationships = {
      "user" : OneToOne("location", "user", "id", "user_id")
   }
```

And you can use the relationship as follow

```

l = Location(name="test location")
l.user = User(name="test user")
l.save()

```

# Launching a query manually

## Executing a single statement

When executing a single statement, you have multiple operations you can do, either insert or retrieve data.
The two have very different intents and are used by the mysql connector differently.

Therefor, when retrieving data or insert (or updating) you will have to use different methods.

### Retrieving data

```
from app.entity_manager import EntityManager
import logging

em = EntityManager()

db = em.db
sql = f.read()
cursor = db.cursor(dictionnary=True)
res = cursor.execute(sql):
if res.row_count > 0:
   #Do something with the data

```

### Inserting data

```
from app.entity_manager import EntityManager
import logging

em = EntityManager()

db = em.db
sql = f.read()
cursor = db.cursor(dictionnary=True)
res = cursor.execute(sql)

db.commit()

print(res.rowcount)
print(res.lastinsertedid)


```

You see the main difference here is that you need to commit your changes to the database.

It's basically the only difference. The usage of ```db.commit()``` at the end of your querying.

## Executing multiple statements
```
from app.entity_manager import EntityManager
import logging

em = EntityManager()

db = em.db
sql = f.read()
cursor = db.cursor()
for result in cursor.execute(sql, multi=True):
   if result.with_rows:
      logging.debug("Rows added by {}".format(result.statement))
      logging.debug(reuslt.fetchall())
   else:
      logging.debug("Rows affected {} by {}".format(result.rowcount,result.statement))
db.commit()

```

## Executing

## Calling a stored procedure

https://www.mysqltutorial.org/calling-mysql-stored-procedures-python/