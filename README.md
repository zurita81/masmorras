# Masmorra — Desafio de Jogos em Python

Plataforma de masmorras em pixel art, feito com **Pygame** para o Desafio de Jogos
do Colégio Estadual André Andreatta.

Inspiração: salas que trancam até derrotar todos os inimigos (estilo Soul Knight),
visual gótico e sombrio (estilo Blasphemous) e um chefe no fim de cada mundo.

## Fases

| Fase | Conteúdo |
|------|----------|
| 1-1  | Introdução, inimigos básicos |
| 1-2  | Novo inimigo, mais salas |
| 1-3  | Dificuldade maior |
| 1-4  | Chefe |

## Personagens

Cavaleiro, Mago, Druida, Arqueiro e Metamorfo (que se transforma em lobo).

## Como rodar

```bash
pip install -r requirements.txt
python src/main.py
```

## Controles

| Ação | Teclas |
|------|--------|
| Mover | Setas ou A / D |
| Pular | Espaço, W, Seta para cima ou Z (segure para pular mais alto) |
| Descer de plataforma fina | Baixo + Pular |
| Tela cheia | F11 |
| Sair | Esc |

## Estrutura

```
src/        código do jogo (main.py é o ponto de entrada)
assets/     sprites, sons e fases (assets/niveis/*.txt são os mapas em texto)
tools/      gerador de sprites e testes automáticos da física
```

Os textos ficam em `src/idiomas.py`; para adicionar um idioma basta copiar o bloco `pt`.

## Testes

```bash
python tools/teste_fisica.py
```

## Regenerar os sprites

```bash
python tools/gerar_sprites.py
```

## Roteiro

1. ✅ Base: janela, jogador, plataformas, câmera (PC)
2. Tiro, inimigos, vidas e pontuação
3. Sistema de salas e fases 1-1 a 1-3
4. Chefe da 1-4
5. Sons, menu e tela de game over
6. Controles de toque e versão web/celular (pygbag)
