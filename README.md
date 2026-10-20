# organiza-downloads

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-6366f1?style=flat-square&labelColor=1e293b&logo=python&logoColor=white) ![cron](https://img.shields.io/badge/cron-6366f1?style=flat-square&labelColor=1e293b) ![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-6366f1?style=flat-square&labelColor=1e293b&logo=opensourceinitiative&logoColor=white)

Script que arruma a minha pasta `~/Downloads`. Cada arquivo solto na raiz vai para
uma subpasta por tipo: `Documentos`, `Imagens`, `Videos`, `Audio`, `Compactados`,
`Codigo`, `Executaveis` e `Fontes`.

Fiz porque a pasta virava depósito em duas semanas — PDF de disciplina no meio de
instalador, print misturado com ISO. Agora roda sozinho pelo cron e eu não preciso
lembrar que ela existe.

## Rodando

Sem dependência externa, só biblioteca padrão (Python 3.8+).

    python3 main.py

No meu caso quem chama é o cron, uma vez por dia:

    0 17 * * * cd "/home/eduardo/projetos/organiza-downloads" && /usr/bin/python3 main.py >> "/home/eduardo/projetos/organiza-downloads/cron.log" 2>&1

O script imprime uma linha de resumo a cada execução. Isso é de propósito: se ele
parar de rodar, o `cron.log` responde rápido — log parado por dias significa cron
morto, e não "não tinha nada pra organizar".

## Decisões que não são óbvias

- **Não sobrescreve nada.** Se já existe `Documentos/contrato.pdf`, o arquivo novo
  entra como `contrato (1).pdf`. Na primeira versão o script apagava o antigo sem
  avisar, e isso eu não queria num script que roda sem eu olhar.
- **Espera 3 minutos.** Arquivo modificado nos últimos `MIN_IDADE_SEGUNDOS` é
  pulado, porque é a janela em que o navegador ainda pode estar escrevendo nele.
  Sem essa espera, mover um download em andamento corrompe o arquivo.
- **Ignora download incompleto e lixo de sistema.** `.crdownload`, `.part`,
  `.partial`, `.tmp` e companhia ficam onde estão, junto com arquivo oculto e as
  travas do Office (`~$relatorio.docx`).
- **Extensão fora da lista não é movida.** Nada de pasta "Outros" juntando arquivo
  sem extensão que eu não sei o que é.
- **Só a raiz.** Subpasta dentro de `~/Downloads` é ignorada de propósito, porque é
  onde eu guardo coisa que estou usando agora.

## Configurando

As categorias são o dict `types` no topo do `main.py`. Para incluir uma extensão
basta editar a lista dela: o índice usado na busca é montado a partir desse dict.

## O que ele não faz

- Não desfaz movimentação. Se categorizar errado, é na mão.
- Não olha o conteúdo do arquivo. Qualquer PDF cai em `Documentos`, inclusive
  boleto e nota fiscal, que eu arquivo em outro lugar.
- Não roda no Windows, porque depende do cron. Lá teria que agendar pelo
  Agendador de Tarefas.
- Não mexe em arquivo que já está em subpasta, nem em pasta que eu criei à mão.

## Testando sem risco

O `main.py` importa sem executar nada (tem guard de `__main__`), então dá para
apontar ele para uma pasta temporária e testar de verdade sem encostar no
`~/Downloads`:

    import importlib.util, tempfile
    from pathlib import Path

    spec = importlib.util.spec_from_file_location("organizador", "main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.organizar(Path(tempfile.mkdtemp()))

Foi assim que testei o tratamento de colisão de nome antes de confiar nele.

## Licença

MIT. Faz o que quiser com o código.
