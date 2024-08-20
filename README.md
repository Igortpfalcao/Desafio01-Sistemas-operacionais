# Baguncinha em Shinjuku

Este é um jogo simples que tenta seguir a lógica básica de um RPG, onde você cria seu personagem, escolhe atributos e luta contra inimigos

O objetivo do jogo é derrotar três chefes antes que o tempo acabe, Uraume, a fiel escudeira de Subuxa, O general divino MAHORAGA, uma das fraudes de Subuxa, e por fim, o próprio Subuxa.

A condição de corrida ocorre quando dois ou mais feiticeiros (que são representados por threads) atacam o chefe ao mesmo tempo, sendo necessário um controle para que a variável da vida seja decrementada
de forma correta, sendo assim, apliquei o MUTEX, e semáforo.

O jogo em semáforo permite que dois feiticeiros acessem a vida do inimigo ao mesmo tempo, colocando seus ataques em uma fila, para enfim decrementar sua vida.


lutar com vários feiticeiros é fácil, mas será que você consegue acabar com as fraudes de Subuxa com poucos números?

