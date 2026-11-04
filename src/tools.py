import unicodedata
from typing import Optional
import pandas as pd
from src.data_loader import db


def _normalize_text(text: str) -> str:
    """Removes accents and converts text to lowercase for accent-insensitive search."""
    if not isinstance(text, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _format_product_row(row: pd.Series) -> str:
    """Formats a single catalog product row with full pricing and stock transparency."""
    promo_info = ""
    if row["has_active_promo"]:
        promo_info = (
            f" | [PROMOÇÃO ATIVA: {row['active_promo_name']} "
            f"({row['active_discount_percent']}% OFF — de R$ {row['price_brl']:,.2f} por R$ {row['final_price_brl']:,.2f})]"
        )
    elif pd.notna(row.get("expired_promo_name")):
        promo_info = (
            f" | [Nota: promoção anterior '{row['expired_promo_name']}' "
            f"de {int(row['expired_discount_percent'])}% está EXPIRADA/INATIVA — preço vigente é o de tabela]"
        )

    pix_note = (
        f"R$ {row['pix_price_brl']:,.2f} (preço promocional, sem desconto PIX cumulativo)"
        if row["has_active_promo"]
        else f"R$ {row['pix_price_brl']:,.2f} (5% de desconto no PIX)"
    )

    return (
        f"- [ID {row['product_id']}] **{row['name']}** (Categoria: {row['category_name']})\n"
        f"  Preço Atual: R$ {row['final_price_brl']:,.2f}{promo_info} | À vista no PIX: {pix_note}\n"
        f"  Estoque: {row['stock_quantity']} un. | Status: {row['status']} | Descrição: {row['description']}"
    )


def search_products(
    query: Optional[str] = None,
    category_id: Optional[int] = None,
    max_price: Optional[float] = None,
    only_available: bool = True
) -> str:
    """
    Searches the Empório da Música instrument catalog with filters for name/description,
    category (1: Guitarras, 2: Baixos, 3: Baterias e Percussão, 4: Teclados e Pianos,
    5: Violões, 6: Instrumentos de Sopro Madeiras, 7: Instrumentos de Sopro Metais,
    8: Cordas Orquestrais, 9: Ukuleles), maximum budget in BRL, and stock availability.
    Returns exact pricing, active discounts, expired promotion warnings, and PIX pricing.
    """
    df = db.catalog_df.copy()

    if category_id is not None:
        df = df[df["category_id"] == category_id]

    if query:
        q_norm = _normalize_text(query)
        stopwords = {"de", "da", "do", "com", "para", "ate", "em", "um", "uma", "o", "a", "os", "as"}
        tokens = [t for t in q_norm.split() if t not in stopwords]

        searchable_series = (
            df["name"].fillna("").apply(_normalize_text) + " " +
            df["description"].fillna("").apply(_normalize_text) + " " +
            df["category_name"].fillna("").apply(_normalize_text) + " " +
            df["specs"].fillna("").apply(_normalize_text)
        )

        for token in tokens:
            stem = token[:-3] if token.endswith("oes") else (token[:-1] if token.endswith("s") and len(token) > 4 else token)
            df = df[searchable_series.loc[df.index].str.contains(stem, na=False, regex=False)]

    if max_price is not None:
        df = df[df["final_price_brl"] <= max_price]

    unavailable_matches = df[df["is_available"] == False] if only_available else pd.DataFrame()

    if only_available:
        df = df[df["is_available"] == True]

    if df.empty:
        if not unavailable_matches.empty:
            unavail_text = "\n".join(_format_product_row(r) for _, r in unavailable_matches.iterrows())
            cat_ids = unavailable_matches["category_id"].unique()
            alt_df = db.catalog_df[
                (db.catalog_df["category_id"].isin(cat_ids)) &
                (db.catalog_df["is_available"] == True)
            ].sort_values("final_price_brl").head(5)
            alt_text = "\n".join(_format_product_row(r) for _, r in alt_df.iterrows())
            return (
                f"[ATENÇÃO] O(s) instrumento(s) buscado(s) encontra(m)-se INDISPONÍVEL(IS) (sem estoque, descontinuado ou em breve):\n"
                f"{unavail_text}\n\n"
                f"[SUGESTÕES] Alternativas disponíveis na mesma categoria para sugerir ao cliente (Seção 7.3):\n{alt_text}"
            )

        return (
            "Nenhum instrumento disponível encontrado com esses filtros exatos. "
            "Tente buscar apenas por category_id ou aumentar a faixa de preço para sugerir alternativas disponíveis."
        )

    df_sorted = df.sort_values("final_price_brl", ascending=True)
    results = [_format_product_row(row) for _, row in df_sorted.head(15).iterrows()]

    header = f"Encontramos {len(df_sorted)} instrumento(s) disponível(is)"
    if len(df_sorted) > 15:
        header += " (exibindo os 15 primeiros ordenados pelo menor preço)"
    return f"{header}:\n" + "\n".join(results)


def check_order_status(
    order_id: Optional[int] = None,
    customer_name: Optional[str] = None
) -> str:
    """
    Checks the status, tracking code, estimated delivery, payment method, and items
    of a customer order using the numerical order_id or customer_name.
    """
    df = db.orders_full_df.copy()

    if order_id is not None:
        df = df[df["order_id"] == order_id]
    elif customer_name is not None:
        cn_norm = _normalize_text(customer_name.strip())
        name_series = df["customer_name"].fillna("").apply(_normalize_text)
        df = df[name_series.str.contains(cn_norm, na=False, regex=False)]
    else:
        return "Por favor, informe o número do pedido (order_id) ou o nome do cliente para consultar no sistema."

    if df.empty:
        return "Nenhum pedido encontrado com esses dados no sistema. Peça para o cliente confirmar o número do pedido ou o nome completo cadastrado."

    status_map = {
        "delivered": "ENTREGUE (delivered)",
        "shipped": "ENVIADO / EM TRÂNSITO (shipped)",
        "confirmed": "CONFIRMADO — AGUARDANDO ENVIO (confirmed)",
        "pending": "PENDENTE DE APROVAÇÃO/PAGAMENTO (pending)",
        "cancelled": "CANCELADO (cancelled)",
    }

    results = []
    for _, row in df.iterrows():
        tracking = (
            row["tracking_code"]
            if pd.notna(row["tracking_code"]) and str(row["tracking_code"]).strip() != ""
            else "Ainda não gerado (disponível após o despacho)"
        )
        delivery = (
            row["estimated_delivery"]
            if pd.notna(row["estimated_delivery"]) and str(row["estimated_delivery"]).strip() != ""
            else "A calcular após o despacho"
        )
        notes = f"\n  - Observações do Sistema: {row['notes']}" if pd.notna(row["notes"]) and str(row["notes"]).strip() != "" else ""
        status_label = status_map.get(str(row["status"]).lower(), str(row["status"]).upper())

        results.append(
            f"[PEDIDO #{row['order_id']}]\n"
            f"  - Cliente: {row['customer_name']} (Cidade: {row['customer_city']} | Tel: {row['customer_phone']})\n"
            f"  - Data do Pedido: {row['order_date']} | Status: **{status_label}**\n"
            f"  - Itens Comprados: {row['items_list']}\n"
            f"  - Valor Total: R$ {row['total_brl']:,.2f} (Forma de Pagamento: {row['payment_method']})\n"
            f"  - Código de Rastreamento: {tracking}\n"
            f"  - Data Estimada de Entrega / Recebimento: {delivery}{notes}"
        )

    return "\n\n".join(results)


def consult_store_policies(topic: str) -> str:
    """
    Searches the Empório da Música internal policy manual (PDF) for official rules regarding
    store hours, address/contacts, payment & installment rules, return/exchange rights,
    shipping rates/deadlines, promotions rules, and warranty.
    """
    topic_norm = _normalize_text(topic)
    stopwords = {
        "de", "da", "do", "das", "dos", "para", "com", "por", "em", "na", "no",
        "a", "o", "as", "os", "e", "ou", "que", "como", "qual", "quais", "loja",
        "politica", "politicas", "regra", "regras", "sobre", "funciona"
    }
    keywords = [w for w in topic_norm.split() if len(w) > 2 and w not in stopwords]

    sections = db.policies_text.split("--- PAGE ")
    scored_sections = []

    for section in sections:
        if not section.strip():
            continue
        sec_norm = _normalize_text(section)
        score = sum(1 for kw in keywords if kw in sec_norm)
        if score > 0:
            scored_sections.append((score, "--- PAGE " + section.strip()))

    if scored_sections:
        scored_sections.sort(key=lambda x: x[0], reverse=True)
        top_matches = [sec for _, sec in scored_sections[:4]]
        return "Trechos oficiais do Manual de Políticas da Loja:\n\n" + "\n\n".join(top_matches)

    return "Manual Completo de Políticas da Loja:\n\n" + db.policies_text


def handle_out_of_scope_request(item_requested: str) -> str:
    """
    Handles requests for accessories or non-instrument items (strings, picks, cables,
    cases, pedals, amplifiers, maintenance services, or off-topic subjects) by politely
    explaining the store's instrument-only scope and suggesting our partner store in Campo Grande/MS.
    """
    return (
        f"Item ou assunto fora de escopo: '{item_requested}'. "
        f"Diretriz oficial (Seção 1 e 7.1): A Empório da Música trabalha EXCLUSIVAMENTE com "
        f"instrumentos musicais (guitarras, baixos, violões, baterias, teclados, sopros, cordas "
        f"orquestrais e ukuleles) e NÃO comercializa acessórios (cordas avulsas, palhetas, cabos, cases, "
        f"pedais, suportes ou amplificadores). Caso o cliente tenha pedido um acessório, redirecione-o "
        f"educadamente para nossa loja parceira em Campo Grande/MS: **Pantanal Music & Acessórios** "
        f"(Av. Afonso Pena, Centro - Tel/WhatsApp: (67) 3322-1000). Caso seja um assunto aleatório fora da música, "
        f"responda com simpatia que você é o assistente especializado em instrumentos musicais da Empório da Música."
    )


AVAILABLE_TOOLS = [
    search_products,
    check_order_status,
    consult_store_policies,
    handle_out_of_scope_request,
]
