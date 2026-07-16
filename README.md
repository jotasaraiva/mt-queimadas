# MT Queimadas

Painel interativo para visualização de focos de incêndio em Unidades de Conservação no estado do Mato Grosso.

## Funcionalidades

- Mapa interativo com focos de incêndio e limites de Unidades de Conservação
- Camada PRODES (desmatamento) via WMS do Terrabrasilis/INPE
- Filtros por Unidade de Conservação, esfera administrativa e município
- Tabela agregada de focos por UF, esfera, município e bioma
- Download dos dados filtrados em CSV

## Dados

- **Unidades de Conservação**: ICMBio e MMA (via WFS/INDE)
- **Focos de fogo**: Terrabrasilis/INPE (últimas 48h)

## Instalação

```bash
uv sync
```

## Execução

```bash
uv run streamlit run main.py
```
