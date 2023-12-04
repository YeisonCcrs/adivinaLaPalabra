#Importacion de librerias
import nltk
import random
import requests
from nltk.corpus import cess_esp
from automata.fa.nfa import NFA # Se importa la clase NFA (trabajando desde colaboratory)

#Listado de palabras en español
nltk.download('cess_esp')
palabras = cess_esp.words()
lista_palabras_origen = list(set(palabras))[:1000]
lista_palabras = [i for i in lista_palabras_origen if not any(caracter.isdigit() for caracter in i) and ("_" not in i)]
print(lista_palabras)

#CONSTRUCCION DEL JUEGO
class Autoadivina:

  def __init__(self):
    self.abecedario = 'abcdefghijklmnñopqrstuvwxyzáéíóú'
    self.texto = self.elegirPalabra()
    self.numLetras = len(self.texto)
    self.definicion = self.obtenerDefinicionPalabra(self.texto)

    #Redefinimos los strings para que puedan ser insertados como argumentos en NFA
    estados_finales = set(self.defStates(self.texto).replace("'", "").split(", "))
    estados = set(self.defStates(self.texto).replace("'", "").split(", "))
    estados.add('q0')
    inputs = set(self.getAbecedario().replace("'", "").split(", "))
    self.nfa = self.initAutomata(estados, inputs, estados_finales)
    print("La palabra escogida tiene: " + str(self.numLetras) + " caracteres\nRecuerde que tiene derecho a 3 pistas, para obtenerlas solo debe escribir 'pista' en la entrada de texto")


  def restart(self):
    self.texto = self.elegirPalabra()
    self.numLetras = len(self.texto)
    self.definicion = self.obtenerDefinicionPalabra(self.texto)
    #Redefinimos los strings para que puedan ser insertados como argumentos en NFA
    estados_finales = set(self.defStates(self.texto).replace("'", "").split(", "))
    estados = set(self.defStates(self.texto).replace("'", "").split(", "))
    estados.add('q0')
    inputs = set(self.getAbecedario().replace("'", "").split(", "))

    self.nfa = self.initAutomata(estados, inputs, estados_finales)
    print("La palabra escogida tiene: " + str(self.numLetras) + " caracteres\nRecuerde que tiene derecho a 3 pistas, para obtenerlas solo debe escribir 'pista' en la entrada de texto")

  #Elegir una palabra aleatoria de la lista
  def elegirPalabra(self):
    rand = random.randint(1,len(lista_palabras))
    texto = lista_palabras[rand].lower()
    return texto

    #Obtiene el abecedario en español para las entradas del automata, retorna un string con el formato que recibe automatalib
  def getAbecedario(self):
    inputSymbols = ''
    for i in self.abecedario:
      inputSymbols+="'"+i+"', "
    return inputSymbols

  #Define el numero de estados segun el tamaño de la palabra, retorna un string con el formato que recibe automatalib
  def defStates(self, texto):
    states = ''
    for i in range(1,self.numLetras+2):
      if i != self.numLetras+1:
        states+="'q" + str(i)+"', "
      else:
        states+="'q" + str(i)+"'"
    return states

  #Crea el cuerpo para definir todas las transiciones segun la palabra, retorna un string con el formato que recibe automatalib
  def makeRepeatTransitions(self):
    #Obteniendo la diferencia del conjunto del abecedario con el conjunto de letras de la palabra dada
    abecedarioSet = set(self.abecedario)
    textoSet=set(self.texto)
    restoAbecedario = list(abecedarioSet.difference(textoSet))
    restoAbecedario.sort()

    stateTransitions = ''  #Iniciamos el string

    #Creando un diccionario para la letra y la posicion en la que se encuentra en la palabra
    posiciones_letras = {}
    for i, char in enumerate(self.texto):
      if char in posiciones_letras:
          posiciones_letras[char].append(i)
      else:
          posiciones_letras[char] = [i]
    #Llenando las trancisiones de cada estado generado por la palabra
    for i in range(0, self.numLetras+1):
      stateTransitions+="'q"+str(i)+"'" ": {"
      for letra, posicion in posiciones_letras.items():
        posiciones_letra = posicion
        estadoDestino=''
        for posicion in posiciones_letra:
          estadoDestino += (f"'q{posicion+1}', ")
        stateTransitions += "'"+letra+"'" ": {" +estadoDestino+ "}, "
      #Agregando la transicion epsilon de cada estado, hacia el estado auxiliar, solo si no es el estado inicial
      if i!=0:
        stateTransitions+="'': {'q"+str(self.numLetras+1)+"'} }, \n"
      else:
        for i in restoAbecedario:
          stateTransitions+= "'"+i+"': {'q"+str(self.numLetras+1)+"'}, " # Si es el estado inicial, hacemos la transicion hacia el auxiliar
        stateTransitions+="}, \n"

    #Agregando el estado auxiliar
    stateTransitions+="'q"+str(self.numLetras+1)+"': {"
    for letra, valor in posiciones_letras.items():
        posiciones_letra = valor
        estadoDestino=''
        for posicion in posiciones_letra:
          estadoDestino += (f"'q{posicion+1}', ")
        stateTransitions += "'"+letra+"'" ": {" +estadoDestino+ "}, "
    for i in restoAbecedario:
      stateTransitions+= "'"+i+"': {'q"+str(self.numLetras+1)+"'}, " #Añadimos las transiciones hacia si mismo
    stateTransitions+="}"

    return stateTransitions #FIn de la funcion

  #Inicializa el automata
  def initAutomata(self,estados, inputs, estados_finales):
    nfa1 = NFA(
        states=estados,
        input_symbols=inputs,
        transitions=eval("{" + self.makeRepeatTransitions() + "}"),  # Convierte la cadena a codigo python valido
        initial_state='q0',
        final_states=estados_finales
    )
    return nfa1

  #Validacion por parte del automata
  def checker(self,cadena,NFA):
    try:
        NFA.validate_input(cadena)
        return [step for step in NFA.validate_input(cadena, step=True)]
    except Exception as e:
        print("Entrada no valida: \n", e)

  #Validación de la salida del autómata
  def validacion(self, intento, NFA):
    recorrido = str(self.checker(intento, NFA))
    # Evaluar la cadena para obtener una lista de conjuntos
    listaRecorrido = eval(recorrido)
    diferencias = recorrido.count("{'q"+str(self.numLetras+1)+"'}")
    if self.numLetras-diferencias==0:
      print('Lo siento, no ha adivinado la palabra, y tampoco hay letras que coincidan en su intento')
    elif diferencias>0:
      print('Lo siento, no ha adivinado la palabra, sin embargo hay ' + str(self.numLetras-diferencias) + ' letras que coinciden')
    else:
      coincidencias = 0
      for i in range(1, self.numLetras+1):
        if "q"+str(i)+"" in list(listaRecorrido[i]):
          coincidencias+=1
      if coincidencias == self.numLetras:
        print('¡Felicidades! usted ha adivinado la palabra: ' + self.texto)
        print('La palabra ' + "'" + self.texto + "'" + ' significa: ' + self.definicion + '\n')
        print("¡Juguemos de nuevo! Recuerda que puedes abandonar el juego escribiendo 'Salir'")
        self.restart()
      else:
        print('Lo siento, no ha adivinado la palabra; sin embargo todas las letras ingresadas están en la palabra y tiene ' + str(coincidencias) + ' coincidencias exactas (letra y posicion). \n Consejo, podría tener letras repetidas, o en el orden inadecuado')

  #Control de la entrada dada por el usuario
  def validacionInput(self, input):
    if len(input) == self.numLetras and input.isalpha():
      self.validacion(input, self.nfa)
    elif len(input) != self.numLetras:
        print('Por favor ingrese una palabra con el numero de caracteres que se le indicó ('+ str(self.numLetras) + ')')
    elif not input.isalpha():
      print('Por favor, no ingrese números ni símbolos en la entrada, solo letras')

  #Buscar definicion API
  def obtenerDefinicionPalabra(self,palabra):
      url = f'https://api.wordreference.com/0.8/80143/json/esen/'+palabra
      respuesta = requests.get(url)
      datos = respuesta.json()
      try:
        definicion = datos['term0']['PrincipalTranslations']['0']['OriginalTerm']['sense']
        return definicion
      except Exception as e:
        return 'No se ha podido encontrar una definicion'

  def pista(self, pistas):
    if pistas==3:
      print('La palabra empieza por: ' + self.texto[0] + ' y termina por: ' + self.texto[self.numLetras-1])
    elif pistas==2:
      print('La palabra significa: ' + self.definicion)
    elif pistas==1:
      print('Así es muy fácil, pero las primeras letras de la palabra son: ' + self.texto[:((int)(self.numLetras/2))])
