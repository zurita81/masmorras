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

Cavaleiro (pronto), Mago, Druida, Arqueiro e Metamorfo (que se transforma em lobo).

## Como rodar

```bash
pip install -r requirements.txt
python src/main.py
```

## Controles

| Ação | Teclas |
|------|--------|
| Mover (8 direções) | Setas ou W A S D |
| Tela cheia | F11 |
| Sair | Esc |

## Estrutura

```
src/        código do jogo (main.py é o ponto de entrada)
assets/     sprites, sons e fases (assets/niveis/*.txt são os mapas em texto)
tools/      gerador de sprites e testes automáticos
```

Os textos ficam em `src/idiomas.py`; para adicionar um idioma basta copiar o bloco `pt`.

Mapas: `#` parede, `.` chão, `P` posição inicial do jogador.

## Sprites e testes

```bash
python tools/gerar_sprites_topo.py   # redesenha os sprites em assets/sprites
python tools/teste_movimento.py      # testes automáticos do movimento
```

## Roteiro

1. ✅ Base: janela, jogador, câmera (PC) — agora em vista de cima
2. Sprites de todos os personagens, ataque, inimigos, vidas e pontuação
3. Sistema de salas que trancam e fases 1-1 a 1-3
4. Chefe da 1-4
5. Sons, menu e tela de game over
6. Controles de toque e versão web/celular (pygbag)

A primeira versão, de plataforma (vista lateral), ficou guardada no histórico do git
(commit "Etapa 1").
