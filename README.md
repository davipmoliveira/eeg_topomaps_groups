# Análise Topográfica de EEG por Grupo

> Análise de sinais de EEG utilizando MNE-Python para geração de mapas topográficos (topomaps) de potência espectral por banda de frequência, comparando diferentes grupos de sujeitos.

##  Descrição

Este repositório contém o código desenvolvido para [TCC de MBA em Inteligência Artificial e Big Data do Instituto De Ciências Matemáticas e de Computação da USP São Carlos  / Visualização espectral agregada de
eletroencefalografia (EEG): um pipeline em MNE-Python para geração de mapas topográficos por grupo], utilizando a biblioteca [MNE-Python](https://mne.tools/stable/index.html) para processamento e visualização de sinais de eletroencefalografia (EEG).

O pipeline:
1. Lê arquivos `.edf` brutos, exclui canais técnicos e aplica filtro passa-banda (0.5–40 Hz), salvando o resultado já anonimizado (`grupo1`...`grupo4`) como `.fif` (ver seção [Pré-processamento](#-pré-processamento-filtragem-dos-dados-brutos))
2. Lê os arquivos `.fif` filtrados, organizados por grupo
3. Padroniza os canais para o padrão 10-20 (+ TP7/TP8)
4. Calcula o espectro de potência (PSD, método Welch) por sujeito
5. Converte para dB e calcula a média por grupo
6. Gera topomaps de potência por banda (Delta, Theta, Alpha, Beta, Gamma)
7. Gera mapas de diferença de cada grupo em relação ao grupo de referência (Grupo1)

**Nota sobre anonimização:** os grupos são identificados apenas como `Grupo1`, `Grupo2`, `Grupo3` e `Grupo4` no código e nas figuras — os dados e sua identificação clínica não são divulgados neste repositório.

##  Pré-processamento (filtragem dos dados brutos)

Antes de rodar o notebook principal, os arquivos `.edf` brutos precisam passar por esta etapa, que:
1. Exclui canais técnicos (que contêm `32` ou `LEAK` no nome)
2. Aplica filtro passa-banda de 0.5–40 Hz
3. Salva o resultado como `.fif`, já com o nome da pasta anonimizado (`grupo1`...`grupo4`)

Organize seus dados brutos localmente assim antes de rodar:
```
dados/convertidos/
├── saudavel/    (arquivos .edf)
├── fibro/       (arquivos .edf)
├── dor/         (arquivos .edf)
└── parkinson/   (arquivos .edf)
```

Script (roda localmente, sem depender de Google Drive ou Colab):
```python
import os
import mne

# Caminhos das pastas no seu computador (ajuste para onde estão seus dados)
pasta_raiz_origem = 'dados/convertidos'
pasta_raiz_destino = 'dados/filtrados'

# Mapeamento: nome real da pasta de origem -> nome anonimizado da pasta de destino.
# Os nomes reais dos grupos só aparecem aqui; a partir da pasta de destino em diante
# (e em todo o resto do notebook de análise), só se usa grupo1..grupo4.
mapeamento_grupos = {
    'saudavel': 'grupo1',
    'fibro': 'grupo2',
    'dor': 'grupo3',
    'parkinson': 'grupo4',
}

for grupo_origem, grupo_destino in mapeamento_grupos.items():
    pasta_grupo_origem = os.path.join(pasta_raiz_origem, grupo_origem)
    pasta_grupo_destino = os.path.join(pasta_raiz_destino, grupo_destino)

    os.makedirs(pasta_grupo_destino, exist_ok=True)

    if not os.path.exists(pasta_grupo_origem):
        print(f" Atenção: A pasta {pasta_grupo_origem} não foi encontrada. Pulando...")
        continue

    arquivos_edf = [f for f in os.listdir(pasta_grupo_origem) if f.endswith('.edf')]
    print(f"\n--- Processando o grupo: {grupo_destino} ({len(arquivos_edf)} sujeitos encontrados) ---")

    for i, nome_arquivo in enumerate(arquivos_edf, start=1):
        caminho_completo_entrada = os.path.join(pasta_grupo_origem, nome_arquivo)
        print(f"   [{i}/{len(arquivos_edf)}] Sujeito: {nome_arquivo}...")

        try:
            raw = mne.io.read_raw_edf(caminho_completo_entrada, preload=True, verbose='WARNING')

            # Exclusão de canais técnicos
            canais_para_excluir = [ch for ch in raw.ch_names if '32' in ch or 'LEAK' in ch.upper()]
            if canais_para_excluir:
                raw.drop_channels(canais_para_excluir)
                print(f"      Canais excluídos: {canais_para_excluir}")

            # Filtro passa-banda (0.5-40 Hz)
            raw.filter(l_freq=0.5, h_freq=40.0, fir_design='firwin', verbose='WARNING')

            # Salvar como .fif na pasta já anonimizada
            nome_saida_fif = nome_arquivo.replace('.edf', '_raw.fif')
            caminho_completo_saida_fif = os.path.join(pasta_grupo_destino, nome_saida_fif)
            raw.save(caminho_completo_saida_fif, overwrite=True, verbose='WARNING')
            print(f"       Sucesso! Salvo em: {grupo_destino}/{nome_saida_fif}")

        except Exception as e:
            print(f"    Erro ao processar o sujeito {nome_arquivo}: {e}")

print("\n Tudo pronto! Todos os 4 grupos foram processados e salvos de forma organizada.")
```

Depois de rodar isso, `dados/filtrados/` vai conter as pastas `grupo1` a `grupo4` — que é exatamente a estrutura que o notebook principal espera em `PASTA_BASE/filtrados/`.

##  Estrutura do repositório

```
.
├── notebooks/
│   └── mba_eeg_davi.ipynb   # Notebook principal da análise
├── data/                     # Dados (NÃO versionado — ver .gitignore)
│   └── .gitkeep
├── results/                  # Figuras geradas (topomaps, mapas de diferença)
│   └── .gitkeep
├── requirements.txt
├── .gitignore
└── README.md
```

##  Instalação

Clone o repositório:
```bash
git clone https://github.com/davipmoliveira/eeg_topomaps_groups
cd eeg_topomaps_groups
```

Crie um ambiente virtual (opcional, mas recomendado) e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

##  Como usar

1. Abra `notebooks/mba_eeg_davi.ipynb` (localmente com Jupyter ou no Google Colab).
2. Organize seus dados `.fif` já filtrados na seguinte estrutura, e ajuste a variável `PASTA_BASE` na célula de configuração para apontar pra ela:
   ```
   PASTA_BASE/
   └── filtrados/
       ├── grupo1/   (.fif do grupo de referência)
       ├── grupo2/
       ├── grupo3/
       └── grupo4/
   ```
3. Rode as células em ordem: instalação → configuração → análise.
4. As figuras (`.png` e `.pdf`, uma por banda de frequência, mais os mapas de diferença) são salvas na pasta `figuras_topomap_final` dentro de `PASTA_BASE`.

### Rodando no Google Colab

Clique no botão abaixo para abrir o notebook diretamente no Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/davipmoliveira/eeg_topomaps_groups/blob/main/notebooks/mba_eeg_davi.ipynb)

##  Dados

Os dados de EEG utilizados neste projeto **não estão incluídos neste repositório** por conterem informações de sujeitos/pacientes. Para reproduzir a análise, é necessário ter seus próprios arquivos `.fif` organizados na estrutura descrita acima. Os canais devem seguir (ou ser mapeáveis para) o padrão 10-20 com os eletrodos: `Fp1, Fp2, F3, F4, C3, C4, P3, P4, O1, O2, F7, F8, T3, T4, T5, T6, Fz, Cz, Pz, TP7, TP8`.

##  Referências

- Gramfort, A., Luessi, M., Larson, E., Engemann, D. A., Strohmeier, D., Brodbeck, C., ... & Hämäläinen, M. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, 7, 267.
- MNE-Python Developers. (2026). *topomap.py* [Código-fonte]. GitHub. https://github.com/mne-tools/mne-python/blob/main/mne/viz/topomap.py
