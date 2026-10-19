# TaxiGreen — Otimização de Frota

Projeto da unidade curricular de **Inteligência Artificial** (Universidade do
Minho, 2024/2025). Simula a gestão de uma frota de táxis elétricos e a
combustão, atribuindo veículos a pedidos dinâmicos de transporte.

## Objetivos

- Formular o problema de alocação de frota como um problema de procura.
- Comparar algoritmos de procura informada e não informada.
- Otimizar custo, tempo de resposta, emissões e satisfação do cliente.
- Considerar trânsito, autonomia, carregamentos e falhas de infraestrutura.

## Estrutura

```text
src/algorithms/    algoritmos de procura e heurísticas
src/models/        cidade, veículos, pedidos e estações
src/simulation/    simulador e métricas
src/strategies/    estratégia de alocação
src/utils/         formulação do problema e utilitários
tests/             testes unitários e de integração
```

## Executar

Requer Python 3.10 ou superior. Na raiz do projeto:

```bash
python3 main.py
```

Os parâmetros da frota, cidade, trânsito, pedidos e algoritmos estão em
[`config.py`](config.py).

## Testes

```bash
python3 -m pytest -q
```

## Documentação

- [`Enunciado.txt`](Enunciado.txt) — enunciado do trabalho.
- [`MANUAL.txt`](MANUAL.txt) — instruções de utilização.
- [`relatorio.pdf`](relatorio.pdf) — relatório final.
