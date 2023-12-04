from autoadivina import Autoadivina
#Funcion jugar
def Play():
  pistas = 3
  juego = Autoadivina()
  while True:
    entrada = input('\n¡Intente adivinar!: ')
    entrada = entrada.lower()
    if entrada == 'salir':
      print('Se ha rendido :c')
      print('La palabra era ' + "'"+ juego.texto + "'" + ' y significa: ' + juego.definicion)
      break
    elif entrada == 'pista':
      if pistas>=1:
        juego.pista(pistas)
        pistas-=1
      else:
        print('Ya no te quedan mas pistas, vamos, así es muy fácil...')
    else:
      juego.validacionInput(entrada)


Play()