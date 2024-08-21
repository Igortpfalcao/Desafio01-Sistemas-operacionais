import threading
import time

class SimpleMutex:
    def __init__(self):
        self.flag = False  # Mutex inicializado como não bloqueado
        self.current_owner = None
    
    def lock(self):
        while True:
            if not self.flag:
                # Tentar adquirir o mutex
                if not self.flag:
                    # Se mutex está disponível, bloquear e definir o proprietário
                    self.flag = True
                    self.current_owner = threading.current_thread()
                    return
            # Se o mutex já está bloqueado, esperar e tentar novamente
            time.sleep(0.01)  # Espera ativa (busy-wait)
    
    def unlock(self):
        # Verificar se o thread atual é o proprietário
        if self.current_owner != threading.current_thread():
            raise RuntimeError("Thread não possui o mutex")
        
        # Liberar o mutex
        self.flag = False
        self.current_owner = None

class Feiticeiro(threading.Thread):
    def __init__(self, nome, ataque, velocidade, inimigo, evolucao_event):
        threading.Thread.__init__(self)
        self.ataque = ataque 
        self.velocidade = velocidade
        self.nome = nome
        self.inimigo = inimigo
        self.nivel = 1
        self.evolucao_event = evolucao_event

    def run(self):
        while self.inimigo.vida > 0:
            self.inimigo.receber_dano(self.ataque, self.nome)
            time.sleep(2 - (0.1 * self.velocidade))
        if self.inimigo.nome == "Sukuna":
            print("Parabéns, Você salvou a sociedade de Subuxa e seus lacaios")
            return
        if self.inimigo.ultimo_golpe == self.nome and self.inimigo.nome != "Sukuna":
            self.evoluir()
        

    def evoluir(self):
        print(f"Parabéns. {self.nome} derrotou {self.inimigo.nome}\n")
        self.nivel += 1
        print(f"{self.nome} evoluiu para o nível {self.nivel} e ganhou mais 10 pontos. Escolha como distribuí-los:")
        pontos = 10
        pontos_ataque = 0
        pontos_velocidade = 0
        while pontos > 0:
            pontos_ataque = int(input(f"Quantos pontos você quer alocar para ataque? (1 ponto = 1 de ataque): "))
            while pontos_ataque > pontos:
                print(f"Você só tem {pontos} pontos disponíveis.")
                pontos_ataque = int(input(f"Quantos pontos você quer alocar para ataque? (1 ponto = 1 de ataque, máximo {pontos}): "))
            pontos -= pontos_ataque
            print(f"Você tem {pontos} pontos disponíveis.")
            if pontos > 0:
                pontos_velocidade = int(input(f"Quantos pontos você quer alocar para velocidade? (1 ponto = 0.1 segundo de redução de tempo de ataque): "))
                while pontos_velocidade > pontos:
                    print(f"Você só tem {pontos} pontos disponíveis.")
                    pontos_velocidade = int(input(f"Quantos pontos você quer alocar para velocidade? (1 ponto = 0.1 segundo de redução de tempo de ataque, máximo {pontos}): "))
                pontos -= pontos_velocidade
        self.velocidade += pontos_velocidade
        self.ataque += pontos_ataque
        print(f"{self.nome} agora tem {self.ataque} de ataque e {self.velocidade} de velocidade de ataque")
        self.evolucao_event.set()

class Inimigo:
    def __init__(self, nome, vida):
        self.nome = nome
        self.vida = vida
        self.ultimo_golpe = None
        self.mutex = SimpleMutex()  # Usar SimpleMutex
    
    def receber_dano(self, dano, nome_Feiticeiro):
        self.mutex.lock()
        try:
            if self.vida > 0:
                self.vida -= dano
                print(f'{nome_Feiticeiro} causou {dano} de dano em {self.nome}.\n')
                print(f'{self.nome} tem {self.vida} de vida restante.')
            if self.vida <= 0:
                print(f'{self.nome} Foi derrotado por {nome_Feiticeiro}')
                self.ultimo_golpe = nome_Feiticeiro
        finally:
            self.mutex.unlock()

def criar_personagens(inimigo):
    feiticeiros = []
    while True:
        nome = input("Digite o nome do feiticeiro (ou 'sair' para terminar): \n")
        if nome.lower() == 'sair':
            break
        pontos = 10
        print("Você tem 10 pontos para distribuir, use-os com sabedoria.\n")
        # Distribuição de pontos
        pontos_ataque = 0
        pontos_velocidade = 0
        while pontos > 0:
            pontos_ataque = int(input(f"Quantos pontos você quer alocar para ataque? (1 ponto = 1 de ataque): "))
            while pontos_ataque > pontos:
                print(f"Você só tem {pontos} pontos disponíveis.")
                pontos_ataque = int(input(f"Quantos pontos você quer alocar para ataque? (1 ponto = 1 de ataque, máximo {pontos}): "))
            pontos -= pontos_ataque
            print(f"Você tem {pontos} pontos disponíveis.")
            if pontos > 0:
                pontos_velocidade = int(input(f"Quantos pontos você quer alocar para velocidade? (1 ponto = 0.1 segundo de redução de tempo de ataque): "))
                while pontos_velocidade > pontos:
                    print(f"Você só tem {pontos} pontos disponíveis.")
                    pontos_velocidade = int(input(f"Quantos pontos você quer alocar para velocidade? (1 ponto = 0.1 segundo de redução de tempo de ataque, máximo {pontos}): "))
            pontos -= pontos_velocidade
            print(f"Você tem {pontos} pontos disponíveis.")
        ataque = pontos_ataque
        velocidade = pontos_velocidade

        feiticeiro = Feiticeiro(nome, ataque, velocidade, inimigo, None)
        feiticeiros.append(feiticeiro)
    return feiticeiros

def jogo_progresso(feiticeiros, inimigos, tempo_limite):
    for inimigo in inimigos:
        print(f"{inimigo.nome} com {inimigo.vida} pontos de vida apareceu. Hora da porradaria.")
        time.sleep(1.5)

        evolucao_event = threading.Event()

        feiticeiros_threads = [Feiticeiro(feiticeiro.nome, feiticeiro.ataque, feiticeiro.velocidade, inimigo, evolucao_event) for feiticeiro in feiticeiros]
        for feiticeiro in feiticeiros_threads:
            feiticeiro.inimigo = inimigo
            feiticeiro.start()
        
        inicio = time.time()
        while time.time() - inicio < tempo_limite and inimigo.vida > 0:
            time.sleep(1)
        
        if inimigo.vida > 0:
            print(f"Tempo esgotado! {inimigo.nome} venceu! agora toda a sociedade jujutsu está arruinada...")
            break
        
        for feiticeiro in feiticeiros:
            if feiticeiro.is_alive():
                feiticeiro.join()

        evolucao_event.wait()

        for i, feiticeiro in enumerate(feiticeiros):
            feiticeiro.ataque = feiticeiros_threads[i].ataque
            feiticeiro.velocidade = feiticeiros_threads[i].velocidade
            feiticeiro.nivel = feiticeiros_threads[i].nivel

if __name__ == "__main__":
    inimigos = [Inimigo("Uraume", 150), Inimigo("Mahoraga", 400), Inimigo("Sukuna", 600)]
    personagens = criar_personagens(inimigos[0])
    jogo_progresso(personagens, inimigos, 30)