from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date, union_all, String
from app.core.database import SessionLocal
from app.models import DimProduto, FactRecebimento, FactSaida
from app.schemas.chart import ChartResponse
from datetime import date, timedelta

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

# Rota para buscar os dados da tabela na tela inicial
@router.get('/telaInicial', response_model=ChartResponse)
async def tabela(db: AsyncSession = Depends(get_db)):
    # ------------ dados para gráfico de barras -------------------
    # subquery para agregar os dados de recebimento
    recebimento_sub = select(
        FactRecebimento.codigo,
        func.sum(FactRecebimento.quant).label('quant_recebimento')
    ).group_by(
        FactRecebimento.codigo
    ).subquery()

    # subquery para agregar os dados de saida
    saida_sub = select(
        FactSaida.codigo,
        func.sum(FactSaida.quant).label('quant_saida')
    ).group_by(
        FactSaida.codigo
    ).subquery()
    query_produtos = (
        select(
            DimProduto.nome_basico.label('produto'),
            (func.coalesce(recebimento_sub.c.quant_recebimento, 0) - func.coalesce(saida_sub.c.quant_saida, 0)).label('quantidade')
        )
        .outerjoin(recebimento_sub, DimProduto.codigo == recebimento_sub.c.codigo)
        .outerjoin(saida_sub, DimProduto.codigo == saida_sub.c.codigo)
        .order_by(DimProduto.nome_basico)
    )

    # ----------- Movimentações --------------------
    subquery_recebimentos = select(
        cast(FactRecebimento.data_receb, Date).label('data_movimentacao'),
        FactRecebimento.quant.label('quantidade'),
        func.cast('Recebimento', String).label('tipo_movimentacao')
    )

    subquery_saidas = select(
        cast(FactSaida.data_saida, Date).label('data_movimentacao'),
        FactSaida.quant.label('quantidade'),
        func.cast('Saida', String).label('tipo_movimentacao')
    )

    # Combinação das duas tabelas anteriores para conseguir todas as datas com as informações necessárias
    union_query = union_all(
        subquery_recebimentos,
        subquery_saidas
    ).subquery('movimentacoes_diarias')

    movimentacoes_query = (
        select(
            union_query.c.data_movimentacao,
            union_query.c.tipo_movimentacao,
            func.sum(union_query.c.quantidade).label('quantidade_total')
        )
        .group_by(
            union_query.c.data_movimentacao,
            union_query.c.tipo_movimentacao
        )
        .order_by(
            union_query.c.data_movimentacao,
            union_query.c.tipo_movimentacao
        )
    )

    try:
        result = await db.execute(query_produtos)
        produtos_result = result.mappings().all()

        result = await db.execute(movimentacoes_query)
        movimentacoes_result = result.mappings().all()
    except Exception as e:
        print('ERRO:', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar dados")

    # --------------- gráfico de barras -------------------
    produtos = [dict(item)['produto'] for item in produtos_result]
    quantidade = [dict(item)['quantidade'] for item in produtos_result]

    # --------------- gráfico de linhas -------------------

    # Organiza as datas da mais antiga a mais nova
    datas_unicas = sorted(list(set(row.data_movimentacao for row in movimentacoes_result)))
    data_minima = datas_unicas[0]
    data_maxima = datas_unicas[-1]
    dias = {}

    delta = data_maxima - data_minima    
    # cria cada chave no dicionário dias
    for i in range(delta.days + 1):
        dia = data_minima + timedelta(days=i)
        dias[dia] = [0, 0]
    
    # Adiciona os dados às datas
    for row in movimentacoes_result:
        item = dict(row)
        if not dias.get(item['data_movimentacao']):
            dias[item['data_movimentacao']] = [0, 0] # cria a chave caso não exista
        dias[item['data_movimentacao']][0 if item['tipo_movimentacao'] == 'Recebimento' else 1] = item['quantidade_total']
    
    # salva os recebimentos e saídas
    recebimentos = []
    saidas = []
    for day in dias.keys():
        recebimentos.append(dias[day][0])
        saidas.append(dias[day][1])
    # Formata os dias
    days = [dia for dia in dias.keys()]

    return ChartResponse(
        categories=produtos,
        values=quantidade,
        receipts=recebimentos,
        issues=saidas,
        days=days
    )
