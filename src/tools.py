import pandas as pd
from pydantic import BaseModel, Field
from src.data_loader import db


# ==========================================
# PYDANTIC SCHEMAS FOR TOOL ARGUMENTS
# ==========================================

class SearchProductsInput(BaseModel):
    query: Optional[str] = Field(None, description="Keywords to search in product names or descriptions (e.g., 'Takamine', 'stratocaster', 'nylon').")
    category_id: Optional[int] = Field(None, description="Category ID to filter by (1: Guitarras, 2: Baixos, 3: Baterias/Percussão, 4: Teclados/Pianos, 5: Violões, 6: Sopro Madeiras, 7: Sopro Metais, 8: Cordas Orquestrais, 9: Ukuleles).")
    max_price: Optional[float] = Field(None, description="Maximum budget price in BRL.")
    only_available: bool = Field(True, description="If True, returns only products currently active and with stock > 0.")


class CheckOrderInput(BaseModel):
    order_id: Optional[int] = Field(None, description="The numerical order ID (e.g., 4).")
    customer_name: Optional[str] = Field(None, description="Customer name or partial name to search orders.")


class CheckPolicyInput(BaseModel):
    topic: str = Field(..., description="The policy topic to search in the manual (e.g., 'troca', 'garantia', 'frete', 'pagamento', 'horario').")


# ==========================================
# TOOL FUNCTIONS (EXECUTED BY THE AGENT)
# ==========================================

def search_products(
    query: Optional[str] = None,
    category_id: Optional[int] = None,
    max_price: Optional[float] = None,
    only_available: bool = True
) -> str:
    """
    Searches the Empório da Música instrument catalog with filters for name/description,
    category, budget limits, and stock availability. Returns exact pricing, active discounts,
    and pix pricing.
    """
    df = db.catalog_df.copy()

    if only_available:
        df = df[df["is_available"] == True]

    if category_id is not None:
        df = df[df["category_id"] == category_id]

    if max_price is not None:
        df = df[df["final_price_brl"] <= max_price]

    if query:
        q = query.lower()
        mask = (
            df["name"].str.lower().str.contains(q, na=False) |
            df["description"].str.lower().str.contains(q, na=False)
        )
        df = df[mask]

    if df.empty:
        return "Nenhum instrumento encontrado com esses critérios no catálogo atual. Sugira alternativas semelhantes ou verifique se o item faz parte do nosso escopo exclusivo de instrumentos musicais."

    results = []
    for _, row in df.head(10).iterrows():
        promo_info = f" (🔥 Promoção: {row['active_promo_name']} - {row['active_discount_percent']}% OFF)" if row["has_active_promo"] else ""
        results.append(
            f"- [ID {row['product_id']}] **{row['name']}** ({row['category_name']})\n"
            f"  Preço: R$ {row['final_price_brl']:,.2f}{promo_info} | À vista no PIX: R$ {row['pix_price_brl']:,.2f}\n"
            f"  Estoque: {row['stock_quantity']} unidades | Status: {row['status']}"
        )

    return f"Encontramos {len(df)} instrumento(s):\n" + "\n".join(results)


def check_order_status(
    order_id: Optional[int] = None,
    customer_name: Optional[str] = None
) -> str:
    """
    Checks the status, tracking code, estimated delivery, and items of a customer order
    using the order ID or customer name.
    """
    df = db.orders_full_df.copy()

    if order_id is not None:
        df = df[df["order_id"] == order_id]
    elif customer_name is not None:
        cn = customer_name.lower()
        df = df[df["customer_name"].str.lower().str.contains(cn, na=False)]
    else:
        return "Por favor, informe o número do pedido (order_id) ou o nome do cliente para que eu possa consultar no sistema."

    if df.empty:
        return "Nenhum pedido encontrado com esses dados no sistema. Peça para o cliente confirmar o número do pedido ou nome cadastrado."

    results = []
    for _, row in df.iterrows():
        tracking = row["tracking_code"] if pd.notna(row["tracking_code"]) and row["tracking_code"] != "" else "Ainda não gerado / Disponível após o despacho"
        delivery = row["estimated_delivery"] if pd.notna(row["estimated_delivery"]) else "A calcular"
        notes = f" | Observações: {row['notes']}" if pd.notna(row["notes"]) else ""
        
        results.append(
            f"📦 **Pedido #{row['order_id']}**\n"
            f"  - Cliente: {row['customer_name']} ({row['customer_city']})\n"
            f"  - Data: {row['order_date']} | Status: **{row['status'].upper()}**\n"
            f"  - Itens: {row['items_list']}\n"
            f"  - Valor Total: R$ {row['total_brl']:,.2f} ({row['payment_method']})\n"
            f"  - Rastreamento: {tracking}\n"
            f"  - Previsão de Entrega: {delivery}{notes}"
        )

    return "\n\n".join(results)


def consult_store_policies(topic: str) -> str:
    """
    Searches the Empório da Música internal policy manual for rules regarding store hours,
    payment methods, installment rules, return/exchange rights, shipping, and warranty.
    """
    topic_lower = topic.lower()
    sections = db.policies_text.split("--- PAGE ")
    
    matched_content = []
    for section in sections:
        if any(keyword in section.lower() for keyword in topic_lower.split()):
            matched_content.append(section.strip())

    if matched_content:
        return "Trechos relevantes do Manual de Políticas da Loja:\n\n" + "\n\n".join(matched_content[:3])
    
    # Fallback to general info if specific keyword is broad
    return (
        f"Consulta sobre políticas ({topic}): A Empório da Música possui diretrizes rígidas baseadas "
        f"no Código de Defesa do Consumidor. Caso precise de detalhes específicos sobre trocas (7 dias para online, "
        f"30 dias para defeito), frete (grátis acima de R$ 500 na região metropolitana de Campo Grande/MS) ou "
        f"formas de pagamento (PIX com 5% de desconto, cartões em até 12x), consulte o manual completo."
    )


def handle_out_of_scope_request(item_requested: str) -> str:
    """
    Handles requests for non-instrument items (such as accessories like cables, strings, picks,
    pedals, amps, cases) by politely redirecting the customer and suggesting our ficticious local partner store.
    """
    return (
        f"A Empório da Música trabalha exclusivamente com instrumentos musicais de qualidade "
        f"(guitarras, baixos, violões, baterias, teclados, sopros, cordas orquestrais e ukuleles), "
        f"não comercializando acessórios como '{item_requested}' (conforme nossa política interna). "
        f"Para esse tipo de item, recomendamos fortemente nossa parceira na região de Campo Grande/MS, "
        f"a **Pantanal Music & Acessórios** (localizada na Av. Afonso Pena, telefone (67) 3322-1000), "
        f"onde você encontrará cabos, cordas, cases e amplificadores com excelente atendimento!"
    )


# List of available tool functions for Gemini SDK binding
AVAILABLE_TOOLS = [
    search_products,
    check_order_status,
    consult_store_policies,
    handle_out_of_scope_request
]