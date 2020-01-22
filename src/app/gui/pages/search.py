from app.gui.page import Page
from app.db.entity_manager import EntityManager

from entities.type_bien import TypeBien
import inquirer
from pprint import pprint
from datetime import datetime
from datetime import timedelta
import termtables as tt
import mysql.connector
from app.utils.path import get_config_path
import json

config = {}
with open(get_config_path("db.json"),"r") as f:
   config = json.load(f)

db = mysql.connector.connect(**config)

def search_():
   def getQueryRes(query):

      cu = db.cursor()
      cu.execute(query)
      return cu.fetchall()
   def insert(query, values):
      cu = db.cursor()
      cu.execute(query, values)
      db.commit()
      return cu.rowcount is 1

   def showMultipleChoice(choices):
      for x in choices.get('interests'):
         print(" -"+x)


   def addAndToQuery(query, fieldName, value):
         if query:
            query += " AND {} = '{}'".format(fieldName, value)
         return query

  
   def createWhere(choices, field, binaryOp="OR"):
      firstLoop = True
      query = ""
      for choice in choices.get('interests'):
         if not firstLoop:
            query += " {} ".format(binaryOp)
         query += "{} = '{}'".format(field, choice)
         firstLoop = False

      return query

   def createWherePosition(answers):
      query = ""
      if answers.get('pays'): 
         query = "pays='{}'".format(answers.get('pays'))

      if answers.get('commune'):
         query = addAndToQuery(query, "commune", answers.get('commune'))

      if answers.get('city') :
         query = addAndToQuery(query, "ville", answers.get('city'))

      if answers.get('postalCode'):
         query = addAndToQuery(query, "npa", answers.get('postalCode'))

      return query

   # https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float
   def isNumber(s):
      try:
         int(s)
         return True
      except ValueError:
         return False
   # use to check date
   def isValidDate(date):
      try:         
         datetime.strptime(date,'%d/%m/%Y')
         return True
      except ValueError:
         return False
   
   # use to check user date input
   def isValidDateOrNone(date):
      if date:
         return isValidDate(date)
      else:
         return True
   def askDate():
      startDate = ""
      duration = -1
      while "check date is empty or valid":
         dateCriteria = inquirer.prompt([
            inquirer.Text('startDate', message="Entrez une date de début", validate=lambda _, x: isValidDateOrNone(x))
         ])
         startDateStr = dateCriteria.get('startDate')
         # Si l'utilisateur fournit une date on lui force à mettre une durée
         if startDateStr:
            startDate = datetime.strptime(startDateStr,'%d/%m/%Y')
            durationCriteria = inquirer.prompt([
               inquirer.Text('duration', message="Entrez une durée (nombre de jours)",
               validate=lambda _, x: isNumber(x)),
            ])
            duration = int(durationCriteria.get('duration'))
            break
         else:
            break    
         print("la date doit être au format jour/mois/annee => eg: 12/12/2020")
      
      return startDate, duration
   def isNumberOrQ(number, maxIdx):
      return (isNumber(number) and int(number) > 0 and int(number) <= maxIdx) or str(number) is "Q"

   def createSearchQuery(fournitreWhere, typeBienWhere, positionWhere, unavailableBienQuery):
    
      searchQuery = "SELECT * FROM search_biens"
      # Si il y a des fourniture, on fait un jointure
      if fournitreWhere:
         searchQuery += " INNER JOIN fourniture ON bien_id = bien_immobilier_id"

      # Si il y a des critères à la recherche on ajoute le mot clé WHERE à la requête
      if fournitreWhere or positionWhere or typeBienWhere or unavailableBienQuery:
         print("***")
         print(fournitureChoices)
         print(positionWhere)
         print(typeBienWhere)
         print(unavailableBienQuery)
         searchQuery += " WHERE "
         print("###")

      
      whereQuery = ""

      # On ajoute les différents critères à la requête
      if fournitreWhere:
         whereQuery += fournitureWhere
      
      if typeBienWhere:
         if whereQuery:
            whereQuery = "(" + whereQuery + ") AND (" + typeBienWhere + ")"
         else:
            whereQuery +=  typeBienWhere 


      if positionWhere:
         if whereQuery:
            whereQuery = "(" + whereQuery + ") AND (" + positionWhere + ")"
         else:
            whereQuery +=  positionWhere

      if unavailableBienQuery:
         if whereQuery:
            whereQuery = "(" + whereQuery + ") AND (" + unavailableBienQuery + ")"
         else:
            whereQuery +=  unavailableBienQuery
         
      
      
      return searchQuery + whereQuery

   # TYPE DE BIEN
   bienChoices = inquirer.prompt([
      inquirer.Checkbox('interests',
                      message="Quel genre de bien cherchez-vous ?",
                      choices=list(map(lambda bien : bien[0], getQueryRes("SELECT * FROM type_bien")))),
   ])


   # FOURNITURE 
   fournitureChoices = inquirer.prompt([
      inquirer.Checkbox('interests',
                      message="Quel genre de fourniture sont nécessaire pour vous ?",
                      choices=list(map(lambda type : type[0], getQueryRes("SELECT nom FROM type_fourniture")))),
   ])

   print("\n")

   positionCriteria = inquirer.prompt([
      inquirer.Text('pays', message="Entrez un pays"),
      inquirer.Text('commune', message="Entrez une commune"),
      inquirer.Text('city', message="Entrez une ville"),
      inquirer.Text('postalCode', message="Entrez une NPA")
   ])
   
   positionWhere = createWherePosition(positionCriteria)
   typeBienWhere = createWhere(bienChoices, "type_bien")
   fournitureWhere = createWhere(fournitureChoices, "nom_fourniture")

   startDate = ""
   duration = ""
   startDate, duration = askDate()

   unavailableBienQuery = ""
   if startDate:
      endDate = startDate + timedelta(days=duration)
      sqlStartDate = startDate.strftime('%Y-%m-%d') # date, pas datetime
      sqlEndDate = endDate.strftime('%Y-%m-%d')

      unavailableBienQuery = "bien_id NOT IN (SELECT DISTINCT bien_immobilier_id FROM location WHERE (date_arrivee BETWEEN {} AND {}) AND (DATE_ADD(date_arrivee, INTERVAL duree DAY) BETWEEN {} AND {})) ".format(sqlStartDate, sqlEndDate, sqlStartDate, sqlEndDate)

   searchQuery = createSearchQuery(fournitureWhere, typeBienWhere, positionWhere, unavailableBienQuery)
   print(searchQuery)

   goodsRes = getQueryRes(searchQuery)
   if(len(goodsRes) == 0):
      print("Aucun resultat")
      input("Tappez une touche pour continuer")
      return False

   
   headerBiens = ["id ", "Cap. person.", "Taille (m²)", "type_bien", "Description", "Rue","Commune", "Etat"]
   
   # affichage des résultat
   while True:
      biens = []
      Page.clear()
      idx = 1
      for good in goodsRes:
         biens.append([idx, good[1], good[2], good[5], good[3], good[9], good[7], good[8]])
         idx = idx + 1
      
      print( tt.to_string(
            data=biens,
            header=headerBiens,
            style=tt.styles.ascii_thin_double,
         ))
      bienIdx = inquirer.prompt([inquirer.Text('bienIdx',
                  message="Sélectionnez un bien (ou q pour quitter) ", validate=lambda _,idx: isNumberOrQ(idx, len(goodsRes))
               )])
      # afficher un bien ou quitter
      if bienIdx.get('bienIdx') is "Q":
         return False

      # TODO afficher toutes les infos
      fournitures = getQueryRes("SELECT * FROM fourniture")
      bienIdx = int(bienIdx.get('bienIdx')) - 1
      print("Info appartement ----------------")
      print("Capacite personne : {}".format(goodsRes[bienIdx][2]))
      print("Taille (m²) : {}".format(goodsRes[bienIdx][1]))
      print("Type bien: {}".format(goodsRes[bienIdx][5]))
      print("Description: {}".format(goodsRes[bienIdx][3]))
      print("Tarif: {}".format(goodsRes[bienIdx][13]))
      print("Charge: {}".format(goodsRes[bienIdx][14]))
      print("Adresse: {} {} {} {} {}".format(goodsRes[bienIdx][9], goodsRes[bienIdx][11], goodsRes[bienIdx][12], goodsRes[bienIdx][7], goodsRes[bienIdx][4]))
      if fournitures:
         print("Fournitures Disponbiles: ")
         for fourniture in fournitures:
            print(" -" + fourniture[4])

      # réserver ? 
      reserver = inquirer.prompt([inquirer.Text("ouiNon", message="Souhaitez-vous réserver ce bien ?", 
                                 validate=lambda _,x: x is "O" or x is "N")])
      
      # si O on réserve autrement on réaffiche les résultats
      if reserver.get('ouiNon') is "O":
         date, duree = askDate()
         # TODO AJOUTER PROCEDURE check dispo (attendre procedure Alois)
         # TODO afficher soit: nouvelle date ou retour search
         g = Gui()
         print(bienIdx)
         goodIdx = bienIdx - 1 
         return insert("INSERT INTO location(date_arrivee, duree, estConfirme, locataire_id, bien_immobilier_id) VALUES(%s, %s, %s, %s, %s)",   (date, duree ,"NULL", g.user.id, goodsRes[goodIdx][0]))

   # index en fonction de la position de la vue 
   # 0 => bien_id
   # 1 => taille
   # 2 => capacite
   # 3 => description
   # 4 => pays
   # 5 => type_bien
   # 6 => proprio_nom
   # 7 => commune
   # 8 => etat
   # 9 => rue
   # 10 => complement_rue
   # 11 => numero
   # 12 => npa
   # 13 => tarif journalier 
   # 14 => charges 


   # POUR LINSTANT ON AFFICHE PAS LES FOURNITURE CAR TROP DE PLACE
   #fournitureRes = getQueryRes("SELECT nom_fourniture FROM fourniture WHERE bien_immobilier_id = {}".format(good[0]))
   # fournitures = ""
   # for fourniture in fournitureRes:
   #    fournitures += fourniture[0]+" "


# Search page
search = Page("search")
search.set_main(search_)