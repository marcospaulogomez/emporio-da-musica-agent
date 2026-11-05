# Agent Interaction Examples

Below are 5 conversations tested with the agent, covering catalog queries, business rules from the store manual (expired promotions, installment rules, shipping, and returns), real-time order lookups, and out-of-scope item handling.

*(Note: The dialogues themselves are in Brazilian Portuguese, as the agent serves customers of Empório da Música in Campo Grande/MS).*

---

## 1. Product catalog search with budget filter
**Scenario:** Searching for available acoustic guitars (`Violões`) up to R$ 1,000.00. The agent filters only items with `status = active` and `stock_quantity > 0` (excluding the out-of-stock *Giannini GF-3D*) and informs the 5% PIX discount.

**Customer:**
> Quais opções de violões disponíveis custando até R$1000?

**Tool called:** `search_products(category_id=5, max_price=1000, only_available=True)`

**Agent:**
> Olá! Tudo bem? Seja bem-vindo(a) à Empório da Música!
>
> Consultei nosso estoque aqui e temos **12 modelos de violões disponíveis** até R$ 1.000,00. Como nenhum deles está com promoção ativa no momento, todos têm **5% de desconto para pagamento à vista no PIX**:
>
> **Violões de Nylon (Acústicos):**
> - **Tagima Memphis AC-39 Nylon Natural:** R$ 429,90 (ou **R$ 408,40** no PIX) — 15 un. em estoque
> - **Rozini RC-104 Nylon Estudante:** R$ 459,90 (ou **R$ 436,90** no PIX) — 10 un. em estoque
> - **Yamaha C40 Nylon Natural:** R$ 599,90 (ou **R$ 569,90** no PIX) — 12 un. em estoque
> - **Giannini GN-15 Nylon Cedr Natural:** R$ 689,00 (ou **R$ 654,55** no PIX) — 6 un. em estoque
> - **Yamaha C70 Nylon Natural:** R$ 849,00 (ou **R$ 806,55** no PIX) — 8 un. em estoque
>
> **Violões de Aço (Acústicos e Eletroacústicos):**
> - **Shelby SN-100 Folk Aço Preto:** R$ 549,00 (ou **R$ 521,55** no PIX) — 5 un. em estoque
> - **Giannini GF-1R Aço Folk Sunburst:** R$ 579,90 (ou **R$ 550,90** no PIX) — 7 un. em estoque
> - **Yamaha F310 Aço Natural:** R$ 699,90 (ou **R$ 664,90** no PIX) — 14 un. em estoque
> - **Tagima Dallas Tuner Aço Natural (com afinador):** R$ 749,00 (ou **R$ 711,55** no PIX) — 9 un. em estoque
> - **Shelby SGD-195E Elétrico Aço Sunburst:** R$ 799,00 (ou **R$ 759,05** no PIX) — 6 un. em estoque
> - **Tagima Woodstock Dreadnought Natural:** R$ 899,00 (ou **R$ 854,05** no PIX) — 11 un. em estoque
>
> **Violão de 7 Cordas:**
> - **Tagima TW-7 7 Cordas Aço Natural:** R$ 999,00 (ou **R$ 949,05** no PIX) — 6 un. em estoque
>
> Você tem preferência por cordas de nylon ou de aço? Se quiser, posso te dar mais detalhes sobre algum deles!

---

## 2. Price lookup & expired promotion handling
**Scenario:** The customer asks for the price of the *Takamine GD20* (ID 95). In `promotions.csv`, this item has a 12% discount entry with `is_active = 0`. The agent informs the current list price transparently, applies the 5% PIX discount, and explains installment options per Section 3 of the manual.

**Customer:**
> Quanto custa o Takamine GD20? Ele ainda tá com aquele desconto de 12%?

**Tool called:** `search_products(query="Takamine GD20")`

**Agent:**
> Olá! O **Takamine GD20 Dreadnought Natural** é um excelente violão, com tampo sólido em cedro e um timbre muito encorpado.
>
> Sendo bem transparente com você: aquela promoção anterior de 12% ("Oferta Especial") já **encerrou** e não está mais ativa no nosso sistema.
>
> Os valores e condições atuais dele são:
> - **Preço de tabela:** R$ 2.199,00 (temos **5 unidades** em estoque)
> - **À vista no PIX (5% de desconto):** **R$ 2.089,05**
> - **No Cartão de Crédito:** em até **12x sem juros de R$ 183,25** (respeitando a parcela mínima de R$ 100,00 para parcelamentos de 7x a 12x). Como a compra passa de R$ 2.000,00, você também pode combinar duas formas de pagamento (ex.: uma parte no PIX e o restante no cartão).
>
> Se você estiver na região metropolitana de Campo Grande, o frete sai grátis para esse valor. Posso separar um para você ou ajudar com mais alguma dúvida?

---

## 3. Non-trivial scenario: order return combining store policy + real-time order lookup
**Scenario:** Across two turns, the customer asks about returning an order due to buyer's remorse and then provides their order details. The agent queries both the policy manual PDF and the orders table (`orders.csv` / `customers.csv`).

**Customer:**
> Me arrependi da minha compra, posso devolver meu pedido?

**Tool called:** `consult_store_policies(topic="arrependimento devolução troca prazo")`

**Agent:**
> Olá! Pode ficar tranquilo(a), nós seguimos o Código de Defesa do Consumidor e vamos te orientar.
>
> Pela nossa política de **Direito de Arrependimento (para compras online)**:
> - Você pode solicitar a devolução em até **7 dias corridos após o recebimento** do produto, sem precisar justificar o motivo.
> - O instrumento precisa estar na **embalagem original, sem sinais de uso** e com todos os acessórios e manuais.
> - O **frete de devolução fica por conta da loja** e o reembolso é feito em até **10 dias úteis** na mesma forma de pagamento usada na compra.
> *(Caso seja apenas troca de modelo ou cor por preferência, o prazo também é de até 7 dias com o produto sem uso na embalagem original).*
>
> Você poderia me informar o **número do seu pedido** ou o seu **nome completo** para eu verificar o status da sua compra no sistema?

**Customer:**
> Sou a Ana Carolina Ferreira, pedido número 8.

**Tool called:** `check_order_status(order_id=8, customer_name="Ana Carolina Ferreira")`

**Agent:**
> Obrigado, Ana Carolina! Localizei o seu **Pedido #8** aqui no sistema:
>
> - **Produto:** 1x Ukulele Kala KA-C Concert Mogno
> - **Valor Total:** R$ 349,90 (pago no débito)
> - **Data do pedido:** 15/02/2026
> - **Status atual:** **Enviado / Em trânsito (`shipped`)**
> - **Código de rastreio:** `BRJL5544332BR`
> - **Previsão de entrega:** 28/02/2026
>
> Como o seu pedido ainda está em trânsito, o prazo de 7 dias corridos só começa a contar a partir do dia em que ele for entregue. Você pode **recusar o recebimento** no ato da entrega (assim ele já volta direto para a loja) ou, se alguém receber o pacote, basta mantê-lo na embalagem original sem uso e entrar em contato conosco em até 7 dias para gerarmos a devolução gratuita e o reembolso dos R$ 349,90.
>
> Posso te ajudar com mais alguma informação sobre esse pedido?

---

## 4. General store information & business hours
**Scenario:** Looking up the store's physical address, contact channels, and operating hours.

**Customer:**
> Qual o endereço da loja e o horário de funcionamento?

**Tool called:** `consult_store_policies(topic="endereço horário funcionamento contato")`

**Agent:**
> Olá! Aqui estão os dados e horários de atendimento da **Empório da Música**:
>
> - **Endereço:** Rua 14 de Maio, 3200 — Centro, Campo Grande/MS (CEP 79202-333)
> - **Telefone / WhatsApp:** (67) 3341-4444 | WhatsApp de Atendimento: (67) 3321-4500
> - **E-mail:** contato@emporiodamusica.com.br
>
> **Horário de Funcionamento (loja física e WhatsApp):**
> - **Segunda a Sexta-feira:** das 09:00 às 18:00
> - **Sábado:** das 09:00 às 13:00
> - **Domingos e Feriados:** Fechado
>
> Se quiser fazer uma visita ou precisar consultar algum instrumento específico antes de vir, é só me chamar!

---

## 5. Out-of-stock product + Out-of-scope request (Accessories)
**Scenario:** The customer asks for an acoustic guitar that has `0` stock (*Giannini GF-3D*, ID 96) and also asks to buy accessories (strings and a P10 cable), which fall outside the store's instrument-only scope.

**Customer:**
> Vocês têm o violão Giannini GF-3D? E quero aproveitar pra comprar um jogo de cordas e um cabo P10.

**Tools called:**
1. `search_products(query="Giannini GF-3D")`
2. `handle_out_of_scope_request(item_requested="jogo de cordas e cabo P10")`

**Agent:**
> Olá! Verifiquei aqui no nosso sistema e tenho dois avisos importantes sobre o seu pedido:
>
> **1. Sobre o violão Giannini GF-3D Dreadnought Sunburst:**
> No momento ele está **temporariamente sem estoque** (0 unidades disponíveis). Porém, temos outras ótimas opções de violões de aço em estoque nessa faixa de preço que podem te atender muito bem:
> - **Giannini GF-1R Aço Folk Sunburst:** R$ 579,90 (ou R$ 550,90 no PIX) — 7 unidades em estoque.
> - **Tagima Dallas Tuner Aço Natural:** R$ 749,00 (ou R$ 711,55 no PIX) — 9 unidades em estoque.
> - **Shelby SGD-195E Elétrico Aço Sunburst:** R$ 799,00 (ou R$ 759,05 no PIX) — 6 unidades em estoque.
> - **Tagima Woodstock Dreadnought Natural:** R$ 899,00 (ou R$ 854,05 no PIX) — 11 unidades em estoque.
>
> **2. Sobre o jogo de cordas e o cabo P10:**
> A Empório da Música trabalha **exclusivamente com instrumentos musicais** e não vende acessórios (como encordoamentos avulsos, cabos, palhetas, cases ou amplificadores). Para comprar as cordas e o cabo, recomendo procurar nossa parceira aqui em Campo Grande, a **Pantanal Music & Acessórios** (Av. Afonso Pena, Centro — Tel/WhatsApp: (67) 3322-1000).
>
> Gostaria de ver mais detalhes de algum desses violões disponíveis para substituir o GF-3D?
