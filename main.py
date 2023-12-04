from autoadivina import Autoadivina
#Funcion jugar
def Play():
  juego = Autoadivina()
  while True:
    entrada = input('\n¡Intente adivinar!: ')
    entrada = entrada.lower()
    if entrada == 'salir':
      print('Se ha rendido :c')
      print('La palabra era ' + "'"+ juego.texto + "'" + ' y significa: ' + juego.definicion)
      break
    elif entrada == 'pista':
      if juego.pistas>=1:
        juego.pista(juego.pistas)
        juego.pistas-=1
      else:
        print('Ya no te quedan mas pistas, vamos, así es muy fácil...')
    else:
      juego.validacionInput(entrada)


Play()