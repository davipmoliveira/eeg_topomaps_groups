"""
Análise Topográfica de EEG por Grupo (MNE-Python)

Gerado a partir do notebook mba_eeg_davi.ipynb.
Antes de rodar: instale as dependências com `pip install -r requirements.txt`
e ajuste a variável PASTA_BASE abaixo para onde estão seus dados.

Nota: a etapa de Pré-processamento usa `google.colab.drive`, disponível
apenas no Google Colab. Se for rodar este script localmente, pule essa
etapa (ela já está comentada abaixo) e aponte PASTA_BASE direto para
seus dados já filtrados.
"""

# # Análise Topográfica de EEG por Grupo (MNE-Python)
#
# Este notebook calcula o espectro de potência (PSD) por banda de frequência para diferentes grupos de sujeitos e gera:
# - Mapas topográficos (topomaps) de potência média por grupo e por banda (Delta, Theta, Alpha, Beta, Gamma)
# - Mapas de diferença de cada grupo clínico em relação ao **Grupo1** (grupo de referência/controle)
#
# **Dados de entrada esperados:** arquivos `.fif` (formato MNE) já pré-processados e filtrados, organizados em subpastas por grupo (ver célula de configuração abaixo). Os dados **não** estão incluídos neste repositório — você precisa apontar `PASTA_BASE` para onde os seus dados estão.

# ## 1. Pré-processamento (rode apenas uma vez)
#
# Esta etapa lê os arquivos `.edf` brutos (já convertidos), aplica:
# 1. Exclusão de canais técnicos (que contêm `32` ou `LEAK` no nome)
# 2. Filtro passa-banda de 0.5–40 Hz
#
# ...e salva o resultado como `.fif` já **anonimizado** (`grupo1`...`grupo4`) na pasta `filtrados/`, que é a pasta usada pelas próximas etapas do notebook.
#
# > Os nomes reais dos grupos (usados nas pastas de origem no Drive) só aparecem no mapeamento `mapeamento_grupos` abaixo. Daqui em diante, em todo o resto do pipeline, só se usa `grupo1`–`grupo4`.
#
# > Se você já tem os dados filtrados e anonimizados prontos, **pule esta célula** e vá direto para a etapa de Configuração.

# --- Célula específica do Google Colab (pré-processamento) ---
# Comentada por padrão: rode-a manualmente apenas no Colab, ou adapte
# para ler seus arquivos .edf localmente sem o google.colab.drive.
# from google.colab import drive
# drive.mount('/content/drive')

# import os
# import mne

# # Pasta raiz no Google Drive onde estão os dados convertidos (.edf)
# # e onde os dados filtrados (.fif) serão salvos
# PASTA_RAIZ_DRIVE = '/content/drive/MyDrive/dados_tcc_mba_06_2026'
# pasta_raiz_origem = os.path.join(PASTA_RAIZ_DRIVE, 'convertidos')
# pasta_raiz_destino = os.path.join(PASTA_RAIZ_DRIVE, 'filtrados')

# # Mapeamento: nome real da pasta de origem -> nome anonimizado da pasta de destino.
# # Os nomes reais dos grupos só aparecem aqui; a partir da pasta de destino em diante
# # (e em todo o resto do notebook), só se usa grupo1..grupo4.
# mapeamento_grupos = {
#     'saudavel': 'grupo1',
#     'fibro': 'grupo2',
#     'dor': 'grupo3',
#     'parkinson': 'grupo4',
# }

# for grupo_origem, grupo_destino in mapeamento_grupos.items():
#     pasta_grupo_origem = os.path.join(pasta_raiz_origem, grupo_origem)
#     pasta_grupo_destino = os.path.join(pasta_raiz_destino, grupo_destino)

#     os.makedirs(pasta_grupo_destino, exist_ok=True)

#     if not os.path.exists(pasta_grupo_origem):
#         print(f" Atenção: a pasta {pasta_grupo_origem} não foi encontrada. Pulando...")
#         continue

#     arquivos_edf = [f for f in os.listdir(pasta_grupo_origem) if f.endswith('.edf')]
#     print(f"\n--- Processando {grupo_destino} ({len(arquivos_edf)} sujeitos encontrados) ---")

#     for i, nome_arquivo in enumerate(arquivos_edf, start=1):
#         caminho_completo_entrada = os.path.join(pasta_grupo_origem, nome_arquivo)
#         print(f"   [{i}/{len(arquivos_edf)}] Sujeito: {nome_arquivo}...")

#         try:
#             raw = mne.io.read_raw_edf(caminho_completo_entrada, preload=True, verbose='WARNING')

#             # ETAPA 1: exclusão de canais técnicos
#             canais_para_excluir = [ch for ch in raw.ch_names if '32' in ch or 'LEAK' in ch.upper()]
#             if canais_para_excluir:
#                 raw.drop_channels(canais_para_excluir)
#                 print(f"      Canais excluídos: {canais_para_excluir}")

#             # ETAPA 2: filtro passa-banda (0.5-40 Hz)
#             raw.filter(l_freq=0.5, h_freq=40.0, fir_design='firwin', verbose='WARNING')

#             # ETAPA 3: salvar como .fif na pasta já anonimizada
#             nome_saida_fif = nome_arquivo.replace('.edf', '_raw.fif')
#             caminho_completo_saida_fif = os.path.join(pasta_grupo_destino, nome_saida_fif)
#             raw.save(caminho_completo_saida_fif, overwrite=True, verbose='WARNING')
#             print(f"      Sucesso! Salvo em: filtrados/{grupo_destino}/{nome_saida_fif}")

#         except Exception as e:
#             print(f"   Erro ao processar o sujeito {nome_arquivo}: {e}")

# print("\nPré-processamento concluído! Dados filtrados e anonimizados salvos em:", pasta_raiz_destino)

# ## 2. Instalação

# !pip install mne  # rode isso no terminal: pip install -r requirements.txt

# ## 3. Configuração
#
# Ajuste **apenas** `PASTA_BASE` abaixo para o caminho onde estão seus dados.
#
# Estrutura de pastas esperada:
# ```
# PASTA_BASE/
# └── filtrados/
#     ├── grupo1/   (arquivos .fif do grupo 1)
#     ├── grupo2/   (arquivos .fif do grupo 2)
#     ├── grupo3/   (arquivos .fif do grupo 3)
#     └── grupo4/   (arquivos .fif do grupo 4)
# ```
#
# > Se você rodou o Passo 1 (Pré-processamento) nesta mesma sessão, `PASTA_BASE` já pode ser igual a `PASTA_RAIZ_DRIVE` — o notebook procura a subpasta `filtrados/` automaticamente.
#
# > Se o Colab pedir para reiniciar a sessão logo após instalar o `mne` (`!pip install mne`), reinicie o runtime antes de rodar as próximas células.

# CONFIGURAÇÃO — ajuste apenas esta célula
import os

# Pasta onde estão os dados já organizados por grupo.
# Estrutura esperada dentro de PASTA_BASE/filtrados/:
#   grupo1/  grupo2/  grupo3/  grupo4/
PASTA_BASE = '/content/drive/MyDrive/dados_tcc_mba_06_2026'  # ajuste para o caminho onde estão seus dados

# Pasta de entrada (dados já filtrados, organizados por grupo)
caminho_base = os.path.join(PASTA_BASE, 'filtrados')

# Pasta de saída das figuras
pasta_saida = os.path.join(PASTA_BASE, 'figuras_topomap_final')
os.makedirs(pasta_saida, exist_ok=True)

print("Pasta de entrada (dados filtrados):", caminho_base)
print("Pasta de saída (figuras):", pasta_saida)

# ## 4. Análise

# ANÁLISE

import mne
import numpy as np
import matplotlib.pyplot as plt

# Silenciar warnings do MNE para limpar o console
mne.set_log_level('ERROR')

# %matplotlib inline  # magic do Jupyter, sem efeito em script .py

# Nomes dos grupos anonimizados (Grupo1..Grupo4).
# O mapeamento para as pastas físicas de dados permanece abaixo,
# mas os nomes/labels usados na análise e nos gráficos não identificam o grupo.
grupos = {
    'Grupo1': os.path.join(caminho_base, 'grupo1'),
    'Grupo2': os.path.join(caminho_base, 'grupo2'),
    'Grupo3': os.path.join(caminho_base, 'grupo3'),
    'Grupo4': os.path.join(caminho_base, 'grupo4')
}

# Nomes usados internamente (chaves acima, ligadas às pastas) x nomes exibidos nos gráficos
nomes_exibicao = {
    'Grupo1': 'Grupo 1',
    'Grupo2': 'Grupo 2',
    'Grupo3': 'Grupo 3',
    'Grupo4': 'Grupo 4'
}

bandas = {
    'Delta (0.5-4 Hz)': (0.5, 4.0),
    'Theta (4-8 Hz)': (4.0, 8.0),
    'Alpha (8-13 Hz)': (8.0, 13.0),
    'Beta (13-30 Hz)': (13.0, 30.0),
    'Gamma (30-40 Hz)': (30.0, 40.0)
}

# Lista fixa de canais que TODOS os sujeitos devem ter (19 do 10-20 + TP7 e TP8)
canais_alvo = [
    'Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2',
    'F7', 'F8', 'T3', 'T4', 'T5', 'T6', 'Fz', 'Cz', 'Pz', 'TP7', 'TP8'
]


# FUNÇÃO AUXILIAR: Processar um único arquivo
# ============================================================

def processar_arquivo(caminho_arquivo):
    try:
        raw = mne.io.read_raw_fif(caminho_arquivo, preload=True, verbose=False)

        # 1. Limpar nomes (remover prefixo "EEG ")
        mapeamento = {ch: ch.replace('EEG ', '').strip() for ch in raw.ch_names}
        raw.rename_channels(mapeamento)

        # 2. Renomear TP3/TP4 para TP7/TP8 (padrão do MNE)
        rename_map = {}
        if 'TP3' in raw.ch_names: rename_map['TP3'] = 'TP7'
        if 'TP4' in raw.ch_names: rename_map['TP4'] = 'TP8'
        if rename_map:
            raw.rename_channels(rename_map)

        # 3. EXCLUSÃO DE CANAIS TÉCNICOS (32, LEAK, etc.)
        canais_para_remover = [
            'CARDI', 'FOTO', 'LEAK', 'Leak', 'leak', '32', 'Pera', 'P300'
        ]
        canais_validos = [ch for ch in raw.ch_names if ch not in canais_para_remover]
        raw = raw.pick(picks=canais_validos)

        # 4. Setar montage
        montage = mne.channels.make_standard_montage('standard_1005')
        raw.set_montage(montage, match_case=False, on_missing='ignore')

        # 5. DUPLA PROTEÇÃO: Manter APENAS os canais da lista 'canais_alvo'
        canais_finais = [ch for ch in canais_alvo if ch in raw.ch_names]

        if len(canais_finais) < 15:
            print(f"Arquivo {caminho_arquivo} tem poucos canais válidos ({len(canais_finais)}). Ignorando.")
            return None, None

        raw = raw.pick(canais_finais)

        # 6. Calcular PSD
        psd = raw.compute_psd(method='welch', fmin=0.5, fmax=40.0)

        return psd, raw.info

    except Exception as e:
        print(f"Erro ao processar {caminho_arquivo}: {e}")
        return None, None


# FUNÇÃO AUXILIAR: Calcular média do grupo (em dB)
# ============================================================

def calcular_media_grupo(caminho_pasta):
    arquivos = [f for f in os.listdir(caminho_pasta) if f.endswith('.fif')]

    if len(arquivos) == 0:
        print(f"Nenhum arquivo .fif encontrado em {caminho_pasta}")
        return None, None, None

    print(f"Processando {len(arquivos)} arquivos de {caminho_pasta}...")

    psds_grupo = []
    info = None
    freqs_ref = None

    for arquivo in arquivos:
        caminho_completo = os.path.join(caminho_pasta, arquivo)
        psd, info = processar_arquivo(caminho_completo)

        if psd is not None:
            psds_grupo.append(psd)
            if freqs_ref is None:
                freqs_ref = psd.freqs  # frequências reais, não estimadas via linspace

    if len(psds_grupo) == 0:
        return None, None, None

    # Empilha os PSDs de todos os sujeitos (potência bruta, em uV²/Hz)
    dados_grupo = np.array([psd.get_data() for psd in psds_grupo])

    # >>> CONVERSÃO PARA dB (10*log10) ANTES DE MEDIAR
    # Evita que sujeitos com potência muito alta dominem a média do grupo.
    # Pequeno epsilon evita log(0) em bins sem energia.
    epsilon = 1e-20
    dados_grupo_db = 10 * np.log10(dados_grupo + epsilon)

    psd_medio_db = dados_grupo_db.mean(axis=0)

    print(f"Média (em dB) calculada para {len(psds_grupo)} sujeitos válidos")
    return psd_medio_db, info, freqs_ref


# PASSO 1: Calcular PSD médio (em dB) para cada grupo
# ============================================================

print("="*60)
print("PASSO 1: Calculando PSD médio (dB) por grupo...")
print("="*60)

psds_medios = {}
info_template = None
freqs_template = None

for nome_grupo, caminho_pasta in grupos.items():
    print(f"\n Grupo: {nome_grupo}")
    psd_medio_db, info, freqs_ref = calcular_media_grupo(caminho_pasta)

    if psd_medio_db is not None:
        psds_medios[nome_grupo] = psd_medio_db
        if info_template is None:
            info_template = info
            freqs_template = freqs_ref

print("\n" + "="*60)
print("PSDs médios (dB) calculados!")
print("="*60)


# FUNÇÃO AUXILIAR: potência média por banda (em dB), para todos os grupos
# ============================================================

def calcular_potencia_por_banda(psds_medios, freqs, bandas_dict):
    """
    Retorna um dicionário: {nome_banda: {nome_grupo: array_por_canal}}
    Já em dB, pronto para plotar.
    """
    resultado = {}
    for nome_banda, (fmin, fmax) in bandas_dict.items():
        mask_freq = (freqs >= fmin) & (freqs <= fmax)
        resultado[nome_banda] = {}
        for nome_grupo, psd_medio_db in psds_medios.items():
            resultado[nome_banda][nome_grupo] = psd_medio_db[:, mask_freq].mean(axis=1)
    return resultado

potencia_por_banda = calcular_potencia_por_banda(psds_medios, freqs_template, bandas)


# PASSO 2: Uma figura por banda (grupos lado a lado), sem título geral,
# com o nome de cada grupo posicionado ABAIXO do respectivo mapa
# ============================================================

print("\n Gerando uma figura por banda (dB, escala unificada por grupo)...")

nomes_grupos_ordenados = list(psds_medios.keys())
n_grupos = len(nomes_grupos_ordenados)

for nome_banda in bandas.keys():
    # >>> ESCALA DE COR UNIFICADA: calculada entre os grupos daquela banda
    valores_banda = np.concatenate(
        [potencia_por_banda[nome_banda][g] for g in nomes_grupos_ordenados]
    )
    vmin_banda = np.percentile(valores_banda, 5)
    vmax_banda = np.percentile(valores_banda, 95)

    # +1 subplot no final, reservado para a barra de cor
    fig, axes = plt.subplots(
        1, n_grupos + 1,
        figsize=(3.2 * n_grupos + 1, 4.3),
        gridspec_kw={'width_ratios': [1] * n_grupos + [0.08]}
    )

    im = None
    for i, nome_grupo in enumerate(nomes_grupos_ordenados):
        media_banda = potencia_por_banda[nome_banda][nome_grupo]

        im, _ = mne.viz.plot_topomap(
            data=media_banda,
            pos=info_template,
            axes=axes[i],
            show=False,
            cmap='RdBu_r',
            contours=6,
            vlim=(vmin_banda, vmax_banda)
        )
        axes[i].set_title(
            nomes_exibicao.get(nome_grupo, nome_grupo),
            fontsize=12, fontweight='bold', y=-0.14, pad=0
        )

    cbar = fig.colorbar(im, cax=axes[-1])
    cbar.set_label('Potência (dB)', fontsize=10)

    plt.tight_layout()

    nome_arquivo = nome_banda.split(' ')[0].lower()
    caminho_png = os.path.join(pasta_saida, f'topomap_{nome_arquivo}.png')
    caminho_pdf = os.path.join(pasta_saida, f'topomap_{nome_arquivo}.pdf')

    plt.savefig(caminho_png, dpi=300, bbox_inches='tight')
    plt.savefig(caminho_pdf, bbox_inches='tight')
    plt.show()

    print(f"Figura salva: {caminho_png} / {caminho_pdf}")

# ============================================================
# PASSO 3: Mapas de Diferença (dB, escala unificada por banda), sem título
# geral, com o nome de cada grupo posicionado ABAIXO do respectivo mapa
# ============================================================

if 'Grupo1' in psds_medios:
    print("\n Gerando Mapas de Diferença (dB)...")
    grupos_doencas = [g for g in ['Grupo2', 'Grupo3', 'Grupo4'] if g in psds_medios]

    bandas_diferenca = {
        'Delta': (0.5, 4.0), 'Theta': (4.0, 8.0),
        'Alpha': (8.0, 13.0), 'Beta': (13.0, 30.0)
    }

    potencia_diferenca_banda = calcular_potencia_por_banda(psds_medios, freqs_template, bandas_diferenca)

    diferencas = {}
    for nome_banda in bandas_diferenca:
        diferencas[nome_banda] = {}
        pot_grupo1 = potencia_diferenca_banda[nome_banda]['Grupo1']
        for nome_doenca in grupos_doencas:
            pot_doenca = potencia_diferenca_banda[nome_banda][nome_doenca]
            diferencas[nome_banda][nome_doenca] = pot_doenca - pot_grupo1

    n_doencas = len(grupos_doencas)

    for nome_banda in bandas_diferenca.keys():
        valores_banda = np.concatenate(
            [diferencas[nome_banda][g] for g in grupos_doencas]
        )
        lim_banda = np.max(np.abs(valores_banda))

        fig, axes = plt.subplots(
            1, n_doencas + 1,
            figsize=(3.2 * n_doencas + 1, 4.3),
            gridspec_kw={'width_ratios': [1] * n_doencas + [0.08]}
        )

        im = None
        for i, nome_doenca in enumerate(grupos_doencas):
            diferenca = diferencas[nome_banda][nome_doenca]

            im, _ = mne.viz.plot_topomap(
                data=diferenca, pos=info_template, axes=axes[i], show=False,
                cmap='RdBu_r', contours=6,
                vlim=(-lim_banda, lim_banda)
            )
            nome_doenca_exibicao = nomes_exibicao.get(nome_doenca, nome_doenca)
            axes[i].set_title(
                nome_doenca_exibicao,
                fontsize=12, fontweight='bold', y=-0.14, pad=0
            )

        cbar = fig.colorbar(im, cax=axes[-1])
        cbar.set_label('Diferença (dB)', fontsize=10)

        plt.tight_layout()

        nome_arquivo = nome_banda.lower()
        caminho_png = os.path.join(pasta_saida, f'diferenca_{nome_arquivo}.png')
        caminho_pdf = os.path.join(pasta_saida, f'diferenca_{nome_arquivo}.pdf')

        plt.savefig(caminho_png, dpi=300, bbox_inches='tight')
        plt.savefig(caminho_pdf, bbox_inches='tight')
        plt.show()

        print(f" Figura salva: {caminho_png} / {caminho_pdf}")

print("\n ANÁLISE CONCLUÍDA!")
print(f"\n Todas as figuras foram salvas permanentemente em:\n{pasta_saida}")
