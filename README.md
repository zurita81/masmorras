# Masmorra — Desafio de Jogos em Python

RPG de ação em masmorras, visto de cima e em pixel art, feito com **Pygame** para o
Desafio de Jogos do Colégio Estadual André Andreatta (categoria RPG).

Inspiração: salas que trancam até derrotar todos os inimigos (estilo Soul Knight),
visual gótico e sombrio (estilo Blasphemous) e um chefe no fim do mundo.

## Fases

| Fase | Conteúdo |
|------|----------|
| 1-1  | Introdução, inimigos básicos |
| 1-2  | Novo inimigo, mais salas |
| 1-3  | Dificuldade maior |
| 1-4  | Chefe |

## Personagens

Todos já desenhados em pixel art (de frente, de costas e de lado, com animação de andar):

| Tecla | Personagem |
|-------|------------|
| 1 | Cavaleiro |
| 2 | Mago |
| 3 | Druida |
| 4 | Arqueiro |
| 5 | Metamorfo (aperte **T** para virar Lobo, mais rápido) |

## Como rodar

```bash
pip install -r requirements.txt
python main.py
```

### Jogar no navegador (sem instalar nada)

A cada atualização na branch `main`, o GitHub compila o jogo para web e publica em
**https://zurita81.github.io/masmorras/** (precisa ativar o Pages uma vez: em
*Settings > Pages > Source* escolher **GitHub Actions**). O mesmo link abre no celular,
mas os controles de toque ainda não existem (vêm numa etapa futura).

## Controles

| Ação | Teclas |
|------|--------|
| Mover (8 direções) | Setas ou W A S D |
| Ligar/desligar o som | M |
| Trocar de personagem | 1 a 5 |
| Virar lobo (só o Metamorfo) | T |
| Tela cheia | F11 |
| Sair | Esc |

## Estrutura

```
main.py     ponto de entrada do jogo
src/        código do jogo
.github/    publicação automática da versão web
assets/     sprites, sons e fases (assets/niveis/*.txt são os mapas em texto)
tools/      gerador de sprites e testes automáticos
```

Os textos ficam em `src/idiomas.py`; para adicionar um idioma basta copiar o bloco `pt`.

Mapas: `#` parede, `.` chão, `P` posição inicial do jogador.

## Sprites, sons e testes

```bash
python tools/gerar_sprites_topo.py   # redesenha os 6 personagens em assets/sprites
python tools/gerar_sons.py           # recria os efeitos sonoros em assets/sons (precisa de ffmpeg)
python tools/teste_movimento.py      # testes automáticos do movimento
```

Os efeitos sonoros (passo, espada, flecha, magia, uivo, moeda, porta da sala, chefe etc.)
são sintetizados por código, no estilo retrô de 8 bits, então não têm direitos autorais.

## Roteiro

1. ✅ Base: janela, jogador, câmera (PC), em vista de cima
2. ✅ Sprites dos 5 personagens + lobo, efeitos sonoros e seleção de personagem
3. Ataque de cada personagem, inimigos, vidas e pontuação
4. Sistema de salas que trancam e fases 1-1 a 1-3
5. Chefe da 1-4
6. Menu, tela de game over e mais sons
7. Controles de toque para celular (a versão web já é publicada automaticamente)

A primeira versão, de plataforma (vista lateral), ficou guardada no histórico do git
(commit "Etapa 1").
