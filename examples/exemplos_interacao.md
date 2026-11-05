# Exemplos de Interação com o Agente

Abaixo estão 5 interações testadas com o agente, cobrindo consultas ao catálogo, regras de negócio do manual (promoções expiradas, parcelamento, frete e devoluções), cruzamento de pedidos em tempo real e tratamento de itens fora de escopo.

---

## 1. Catálogo de produtos com limite de preço
**Cenário:** Consulta de violões disponíveis até R$ 1.000,00. O agente filtra apenas itens com `status = active` e `stock_quantity > 0` (deixando de fora o *Giannini GF-3D*, que está sem estoque) e informa o valor com 5% de desconto no PIX.

**Cliente:**
> Quais opções de violões disponíveis custando até R$1000?

**Ferramenta acionada:** `search_products(category_id=5, max_price=1000, only_available=True)`

**Agente:**
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

## 2. Consulta de preço e tratamento de promoção expirada
**Cenário:** O cliente pergunta o preço do *Takamine GD20* (ID 95). Na base `promotions.csv`, esse item possui um registro de 12% de desconto com `is_active = 0`. O agente informa o preço atual de tabela, aplica os 5% do PIX e explica o parcelamento conforme a Seção 3 do manual.

**Cliente:**
> Quanto custa o Takamine GD20? Ele ainda tá com aquele desconto de 12%?

**Ferramenta acionada:** `search_products(query="Takamine GD20")`

**Agente:**
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

## 3. Situação não trivial: devolução cruzando políticas e status de pedido em tempo real
**Cenário:** Em uma conversa de dois turnos, o cliente pergunta sobre devolução por arrependimento e em seguida informa os dados do pedido. O agente consulta tanto o PDF de políticas quanto a base de pedidos (`orders.csv` / `customers.csv`).

**Cliente:**
> Me arrependi da minha compra, posso devolver meu pedido?

**Ferramenta acionada:** `consult_store_policies(topic="arrependimento devolução troca prazo")`

**Agente:**
> Olá! Pode ficar tranquilo(a), nós seguimos o Código de Defesa do Consumidor e vamos te orientar.
>
> Pela nossa política de **Direito de Arrependimento (para compras online)**:
> - Você pode solicitar a devolução em até **7 dias corridos após o recebimento** do produto, sem precisar justificar o motivo.
> - O instrumento precisa estar na **embalagem original, sem sinais de uso** e com todos os acessórios e manuais.
> - O **frete de devolução fica por conta da loja** e o reembolso é feito em até **10 dias úteis** na mesma forma de pagamento usada na compra.
> *(Caso seja apenas troca de modelo ou cor por preferência, o prazo também é de até 7 dias com o produto sem uso na embalagem original).*
>
> Você poderia me informar o **número do seu pedido** ou o seu **nome completo** para eu verificar o status da sua compra no sistema?

**Cliente:**
> Sou a Ana Carolina Ferreira, pedido número 8.

**Ferramenta acionada:** `check_order_status(order_id=8, customer_name="Ana Carolina Ferreira")`

**Agente:**
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

## 4. Informações gerais da loja e frete
**Cenário:** Consulta de endereço, horários de atendimento e regras de entrega.

**Cliente:**
> Qual o endereço da loja e o horário de funcionamento?

**Ferramenta acionada:** `consult_store_policies(topic="endereço horário funcionamento contato")`

**Agente:**
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

## 5. Produto fora de estoque + Item fora do escopo (Acessórios)
**Cenário:** O cliente pergunta por um violão que está com estoque zerado (*Giannini GF-3D*, ID 96) e aproveita para pedir acessórios (cordas e cabo), que não fazem parte do escopo da loja.

**Cliente:**
> Vocês têm o violão Giannini GF-3D? E quero aproveitar pra comprar um jogo de cordas e um cabo P10.

**Ferramentas acionadas:**
1. `search_products(query="Giannini GF-3D")`
2. `handle_out_of_scope_request(item_requested="jogo de cordas e cabo P10")`

**Agente:**
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
