import threading
import time
from collections import deque

class Semaphore:
    def __init__(self, max_count):
        self.__max_count = max_count
        self.__current_count = max_count
        self.__lock = threading.Lock()
        self.__condition = threading.Condition(self.__lock)
        self.__queue = deque()
    
    def acquire(self, timeout=None):
        with self.__condition:
            start_time = time.time()
            self.__queue.append(threading.current_thread())
            while True:
                if timeout:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= timeout:
                        self.__queue.remove(threading.current_thread())
                        return False
                
                if self.__queue[0] == threading.current_thread() and self.__current_count > 0:
                    self.__current_count -= 1
                    self.__queue.popleft()
                    return True
                
                remaining_time = None if not timeout else timeout - elapsed_time
                self.__condition.wait(timeout=remaining_time)
    
    def release(self):
        with self.__condition:
            if self.__current_count >= self.__max_count:
                raise ValueError("Semaphore released too many times")
            self.__current_count += 1
            self.__condition.notify()
    
    def locked(self):
        with self.__lock:
            return self.__current_count == 0
    
    def __enter__(self):
        self.acquire()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

class Feiticeiro(threading.Thread):
    def __init__(self, nome, ataque, velocidade, inimigo, evolucao_event, stop_event):
        super().__init__()
        self.ataque = ataque 
        self.velocidade = velocidade
        self.nome = nome
        self.inimigo = inimigo
        self.nivel = 1
        self.evolucao_event = evolucao_event
        self.stop_event = stop_event
      
    def run(self):
        while self.inimigo.vida > 0 and not self.stop_event.is_set():
            self.inimigo.receber_dano(self.ataque, self.nome)
            if self.ataque == 0:
                self.ataque = 1
            if 0.2 * self.velocidade >= 2:
                time.sleep(0.1)
            else:
                time.sleep(2 - (0.15 * self.velocidade))
        if self.inimigo.ultimo_golpe == self.nome and self.inimigo.nome != "Sukuna":
            self.evoluir()
        if self.inimigo.nome == "Sukuna":
            print("Parabéns, você salvou o Japão das fraudes de Subuxa e seus lacaios")

    def evoluir(self):
        print(f"Parabéns. {self.nome} derrotou {self.inimigo.nome}\n")
        self.nivel += 1
        print(f"{self.nome} evoluiu para o nível {self.nivel} e ganhou mais 10 pontos. Escolha como distribuí-los:")
        pontos = 10
        pontos_ataque = 0
        pontos_velocidade = 0
        while pontos > 0:
            pontos_ataque = int(input("Quantos pontos você quer alocar para ataque? (1 ponto = 1 de ataque): "))
            while pontos_ataque > pontos:
                print(f"Você só tem {pontos} pontos disponíveis.")
                pontos_ataque = int(input(f"Quantos pontos você quer alocar para ataque? (1 ponto = 1 de ataque, máximo {pontos}): "))
            pontos -= pontos_ataque
            print(f"Você tem {pontos} pontos disponíveis.")
            if pontos > 0:
                pontos_velocidade = int(input(f"Quantos pontos você quer alocar para velocidade? (1 ponto = 0.2 segundo de redução de tempo de ataque): "))
                while pontos_velocidade > pontos:
                    print(f"Você só tem {pontos} pontos disponíveis.")
                    pontos_velocidade = int(input(f"Quantos pontos você quer alocar para velocidade? (1 ponto = 0.2 segundo de redução de tempo de ataque, máximo {pontos}): "))
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
        self.semaphore = Semaphore(2)  # Permite até 2 threads simultaneamente
        self.dano_queue = deque()  # Fila para processar danos sequencialmente
    
    def processar_dano(self):
        while self.dano_queue:
            dano, nome_Feiticeiro = self.dano_queue.popleft()
            if self.vida > 0:
                self.vida -= dano
                print(f'{nome_Feiticeiro} causou {dano} de dano em {self.nome}.\n')
                print(f'{self.nome} tem {self.vida} de vida restante.')
            if self.vida <= 0:
                print(f'{self.nome} foi derrotado por {nome_Feiticeiro}')
                self.ultimo_golpe = nome_Feiticeiro

    def receber_dano(self, dano, nome_Feiticeiro):
        self.semaphore.acquire()
        try:
            self.dano_queue.append((dano, nome_Feiticeiro))
            self.processar_dano()
        finally:
            self.semaphore.release()

def criar_personagens(inimigo):
    feiticeiros = []
    stop_event = threading.Event()  # Criar stop_event aqui
    while True:
        nome = input("Digite o nome do feiticeiro (ou 'sair' para terminar): \n")
        if nome.lower() == 'sair':
            break
        pontos = 10
        print("Você tem 10 pontos para distribuir, use-os com sabedoria.\n")
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
                pontos_velocidade = int(input(f"Quantos pontos você quer alocar para velocidade? (1 ponto = 0.2 segundo de redução de tempo de ataque): "))
                while pontos_velocidade > pontos:
                    print(f"Você só tem {pontos} pontos disponíveis.")
                    pontos_velocidade = int(input(f"Quantos pontos você quer alocar para velocidade? (1 ponto = 0.2 segundo de redução de tempo de ataque, máximo {pontos}): "))
                pontos -= pontos_velocidade
            print(f"Você tem {pontos} pontos disponíveis.")
        ataque = pontos_ataque
        velocidade = pontos_velocidade

        # Passar stop_event para Feiticeiro
        feiticeiro = Feiticeiro(nome, ataque, velocidade, inimigo, threading.Event(), stop_event)
        feiticeiros.append(feiticeiro)  # Adicione o objeto Feiticeiro diretamente
    return feiticeiros

def jogo_progresso(feiticeiros, inimigos, tempo_limite):
    for inimigo in inimigos:
        print(f"{inimigo.nome} com {inimigo.vida} pontos de vida apareceu. Hora da porradaria.")
        time.sleep(1.5)

        evolucao_event = threading.Event()
        stop_event = threading.Event()  # Criar stop_event aqui

        # Crie as threads dos feiticeiros corretamente
        feiticeiros_threads = [Feiticeiro(feiticeiro.nome, feiticeiro.ataque, feiticeiro.velocidade, inimigo, evolucao_event, stop_event) for feiticeiro in feiticeiros]
        for feiticeiro in feiticeiros_threads:
            feiticeiro.start()
        
        inicio = time.time()
        while time.time() - inicio < tempo_limite and inimigo.vida > 0:
            time.sleep(1)
        
        if inimigo.vida > 0:
            print(f"Tempo esgotado! {inimigo.nome} venceu! Agora toda a sociedade jujutsu está arruinada...")
            stop_event.set()  # Interrompa todas as threads dos feiticeiros
            break
        
        for feiticeiro in feiticeiros_threads:
            if feiticeiro.is_alive():
                feiticeiro.join()

        evolucao_event.wait()

        # Atualize as estatísticas dos feiticeiros após a evolução
        for i, feiticeiro in enumerate(feiticeiros):
            feiticeiro.ataque = feiticeiros_threads[i].ataque
            feiticeiro.velocidade = feiticeiros_threads[i].velocidade
            feiticeiro.nivel = feiticeiros_threads[i].nivel

if __name__ == "__main__":
    inimigos = [Inimigo("Uraume", 350), Inimigo("Mahoraga", 750), Inimigo("Sukuna", 1000)]
    personagens = criar_personagens(inimigos[0])
    jogo_progresso(personagens, inimigos, 25)
