# 💬 Exemplos de Interação com o Agente — Empório da Música

Abaixo estão **5 conversas completas** demonstrando o comportamento do agente `EmporioMusicAgent` em diferentes cenários operacionais, incluindo consultas em tempo real às tabelas `.csv`, aplicação rigorosa das regras de negócio do manual `politicas_da_loja.pdf`, cruzamento de dados de pedidos e acionamento de *guardrails* de escopo.

---

## Cenário 1: Consulta ao Catálogo com Filtro de Orçamento
**Objetivo demonstrado:** Uso da ferramenta `search_products(category_id=5, max_price=1000.0, only_available=True)`, filtrando automaticamente itens sem estoque (como o *Giannini GF-3D*, que possui `stock_quantity = 0`) e aplicando o desconto de 5% no PIX.

> **👤 Cliente:** Olá! Quais opções de violões disponíveis vocês têm custando até R$ 1.000?

> **🛠️ Tool Call Executada:**
> `search_products(query="violões", category_id=5, max_price=1000.0, only_available=True)`

> **🎵 Empório da Música:**
> Olá! Tudo bem? Seja muito bem-vindo(a) à **Empório da Música**! 🎸 Que alegria ajudar você a escolher seu próximo violão!
>
> Consultei nosso estoque agora mesmo e temos **12 modelos disponíveis** na faixa de até **R$ 1.000,00**, divididos entre cordas de **nylon** (ótimos para iniciantes, MPB e clássico), **aço** (som mais brilhante e encorpado) e até **7 cordas**. Como nenhum deles está em campanha promocional ativa no momento, **todos contam com 5% de desconto para pagamento à vista no PIX**:
>
> ### 🎶 Violões de Nylon (Acústicos)
> 1. **Tagima Memphis AC-39 Nylon Natural** — **R$ 429,90** *(ou **R$ 408,41** no PIX)* | Estoque: 15 un.
>    *Leve e super confortável, perfeito para quem está começando.*
> 2. **Rozini RC-104 Nylon Estudante** — **R$ 459,90** *(ou **R$ 436,91** no PIX)* | Estoque: 10 un.
>    *Feito com madeiras nacionais e acabamento caprichado.*
> 3. **Yamaha C40 Nylon Natural** — **R$ 599,90** *(ou **R$ 569,91** no PIX)* | Estoque: 12 un.
>    *Um clássico mundial para estudo, excelente projeção sonora.*
> 4. **Giannini GN-15 Nylon Cedro Natural** — **R$ 689,00** *(ou **R$ 654,55** no PIX)* | Estoque: 6 un.
>    *Tampo em cedro com sonoridade quente e encorpada.*
> 5. **Yamaha C70 Nylon Natural** — **R$ 849,00** *(ou **R$ 806,55** no PIX)* | Estoque: 8 un.
>    *Nível intermediário com tampo em Spruce sólido e timbre super equilibrado.*
>
> ### 🎸 Violões de Aço (Folk / Dreadnought / Eletroacústico)
> 6. **Shelby SN-100 Folk Aço Preto** — **R$ 549,00** *(ou **R$ 521,55** no PIX)* | Estoque: 5 un.
> 7. **Giannini GF-1R Aço Folk Sunburst** — **R$ 579,90** *(ou **R$ 550,91** no PIX)* | Estoque: 7 un.
> 8. **Yamaha F310 Aço Natural** — **R$ 699,90** *(ou **R$ 664,91** no PIX)* | Estoque: 14 un.
> 9. **Tagima Dallas Tuner Aço Natural (com afinador)** — **R$ 749,00** *(ou **R$ 711,55** no PIX)* | Estoque: 9 un.
> 10. **Shelby SGD-195E Elétrico Aço Sunburst** — **R$ 799,00** *(ou **R$ 759,05** no PIX)* | Estoque: 6 un. *(Eletroacústico com captação e afinador!)*
> 11. **Tagima Woodstock Dreadnought Natural** — **R$ 899,00** *(ou **R$ 854,05** no PIX)* | Estoque: 11 un.
>
> ### 🎼 Violão de 7 Cordas
> 12. **Tagima TW-7 7 Cordas Aço Natural** — **R$ 999,00** *(ou **R$ 949,05** no PIX)* | Estoque: 6 un.
>
> Você prefere cordas de **nylon** (mais macias para os dedos) ou de **aço**? Se quiser, posso te ajudar a comparar os melhores modelos para o estilo que você toca! 😊

---

## Cenário 2: Consulta de Preço + Tratamento de Promoção Expirada e Regras de Parcelamento
**Objetivo demonstrado:** Consulta de um item específico (`Takamine GD20`, ID 95) que possui uma promoção expirada no banco (`is_active == 0` em `promotions.csv`), garantindo transparência total (Seção 6.2 e 7.3) e aplicando as regras de parcelamento e frete (Seção 3.1 e 5.1).

> **👤 Cliente:** Quanto custa o Takamine GD20? Ele ainda está naquela promoção de 12% de desconto?

> **🛠️ Tool Call Executada:**
> `search_products(query="Takamine GD20")`
> `consult_store_policies(topic="parcelamento pagamento")`

> **🎵 Empório da Música:**
> Olá! O **Takamine GD20 Dreadnought Natural** é um violão espetacular — tem tampo sólido em cedro, fundo e laterais em Sapele e um timbre quente incrível para *fingerstyle*! 🎶
>
> Verifiquei aqui no nosso sistema eos detalhes atualizados dele são:
>
> - **Sobre a promoção de 12% ("Oferta Especial"):** Sendo 100% transparente com você, essa campanha promocional já **encerrou** e não está mais ativa no sistema.
> - **Preço Atual de Tabela:** **R$ 2.199,00** *(temos **5 unidades** em estoque para pronta-entrega!)*.
> - **Valor à vista no PIX (5% de desconto):** **R$ 2.089,05** *(como ele não está em promoção ativa, você garante os 5% de desconto do PIX, economizando R$ 109,95!)*.
> - **Parcelamento no Cartão de Crédito:** Em até **12x sem juros de R$ 183,25** (respeitando nossa parcela mínima de R$ 100,00 para planos de 7x a 12x).
> - **Pagamento Combinado:** Como o valor passa de R$ 2.000,00, você também pode combinar duas formas de pagamento (por exemplo, dar uma entrada no PIX e parcelar o restante no cartão)!
>
> Ah, e se você estiver na **Região Metropolitana de Campo Grande/MS**, o **frete é totalmente grátis** (compras acima de R$ 500,00), com entrega em 1 a 3 dias úteis pelo nosso motoboy próprio! Gostaria de garantir o seu?

---

## Cenário 3: Situação Não Trivial — Pedido de Devolução Cruzando Política + Status do Pedido em Tempo Real
**Objetivo demonstrado:** O agente combina a leitura do manual de políticas (`consult_store_policies`) com a busca de pedidos em tempo real (`check_order_status`) em uma conversa multi-turno, analisando datas, status e modalidade da compra.

> **👤 Cliente:** Me arrependi da minha compra, posso devolver meu pedido?

> **🛠️ Tool Call Executada:**
> `consult_store_policies(topic="arrependimento devolução troca prazo")`

> **🎵 Empório da Música:**
> Olá! Fique tranquilo(a), nós seguimos rigorosamente o Código de Defesa do Consumidor e vamos te ajudar com isso! 🤝
>
> Funciona assim aqui na **Empório da Música**:
> 1. **Direito de Arrependimento (Compras Online — Seção 4.1):** Você pode solicitar a devolução em até **7 (sete) dias corridos após o recebimento** do produto, sem precisar de justificativa.
>    - O instrumento precisa estar na **embalagem original, sem sinais de uso** e com todos os acessórios e manuais.
>    - O **frete de devolução é por conta da loja** e o **reembolso é feito em até 10 dias úteis** na mesma forma de pagamento original.
> 2. **Troca por Preferência (Seção 4.3):** Se preferir trocar por outro modelo, cor ou tamanho, também fazemos em até **7 dias**, desde que o instrumento esteja em perfeito estado e na embalagem original.
> *(Observação: instrumentos personalizados sob encomenda, itens de liquidação marcados como "venda final" e boquilhas de sopro por higiene não são elegíveis para troca).*
>
> Você poderia me informar o **número do seu pedido** ou o seu **nome completo**? Assim já consulto a situação exata da sua compra agora mesmo no sistema!

> **👤 Cliente:** Meu nome é Ana Carolina Ferreira, acho que é o pedido número 8.

> **🛠️ Tool Call Executada:**
> `check_order_status(order_id=8, customer_name="Ana Carolina Ferreira")`

> **🎵 Empório da Música:**
> Obrigado por confirmar, **Ana Carolina**! Localizei o seu pedido aqui no sistema:
>
> 📦 **Resumo do Pedido #8**
> - **Item:** 1x Ukulele **Kala KA-C Concert Mogno**
> - **Valor Total:** R$ 349,90 (Pago no Cartão de Débito)
> - **Data do Pedido:** 15/02/2026
> - **Status Atual:** **ENVIADO / EM TRÂNSITO (`shipped`)**
> - **Código de Rastreamento:** `BRJL5544332BR`
> - **Previsão de Entrega:** 28/02/2026
>
> **Como proceder no seu caso:**
> Como o seu pedido ainda está **em trânsito** (ainda não foi entregue), o prazo de **7 dias corridos** do Direito de Arrependimento só começa a contar a partir do momento em que você receber o produto!
>
> Você tem duas opções super simples:
> 1. **Recusar a entrega** no momento em que o entregador chegar, para que o instrumento retorne diretamente para nós; **ou**
> 2. **Receber o pacote** (mantendo-o lacrado/sem uso na embalagem original) e nos avisar em até 7 dias corridos para gerarmos a coleta/logística reversa sem custo para você. Assim que o instrumento retornar, faremos o reembolso integral dos **R$ 349,90** na sua conta em até **10 dias úteis**.
>
> Prefere que eu já deixe uma observação registrada no seu atendimento para acompanhar a devolução?

---

## Cenário 4: Informações Gerais da Loja (Endereço, Horários e Frete)
**Objetivo demonstrado:** Consulta de informações institucionais e logísticas no PDF (`consult_store_policies`).

> **👤 Cliente:** Qual o endereço e o horário de funcionamento da loja? Vocês entregam em Dourados/MS?

> **🛠️ Tool Call Executada:**
> `consult_store_policies(topic="endereço horario funcionamento entrega frete cidades")`

> **🎵 Empório da Música:**
> Olá! Será um prazer receber sua visita ou enviar seu instrumento até Dourados! 🎶 Confira nossas informações:
>
> ### 📍 Endereço e Contatos
> - **Endereço:** Rua 14 de Maio, 3200 — Centro, Campo Grande - MS (CEP 79202-333)
> - **Telefone / WhatsApp Geral:** (67) 3341-4444
> - **Canal de Atendimento WhatsApp:** (67) 3321-4500
> - **E-mail:** contato@emporiodamusica.com.br
>
> ### 🕒 Horário de Funcionamento (Loja Física e WhatsApp)
> - **Segunda a Sexta-feira:** 09:00 às 18:00
> - **Sábado:** 09:00 às 13:00
> - **Domingo e Feriados:** Fechado *(em datas especiais como Black Friday, Aniversário da Loja e Natal, o horário pode ser estendido)*.
>
> ### 🚚 Entregas para Dourados/MS e Outras Cidades
> Sim, enviamos para **Dourados** e todo o Brasil com **seguro contra extravios e danos incluído** e **código de rastreamento** enviado por e-mail e WhatsApp! Trabalhamos com três modalidades:
> - **SEDEX (Correios):** 2 a 5 dias úteis
> - **Jadlog (.package):** 3 a 8 dias úteis
> - **PAC (Correios):** 5 a 12 dias úteis
>
> O valor do frete é calculado de acordo com o CEP, peso e dimensões do instrumento. Tem algum instrumento específico que você gostaria de cotar? 😊

---

## Cenário 5: Produto Fora de Estoque + Guardrail de Itens Fora do Escopo (Acessórios)
**Objetivo demonstrado:** O cliente pede simultaneamente um violão que está com estoque zerado (`Giannini GF-3D`, ID 96, `stock_quantity == 0`) e acessórios (`encordoamento`, `cabo P10`, `amplificador`). O agente aplica a Seção 7.3 (sugerindo substitutos em estoque) e a Seção 1 / 7.1 (redirecionando acessórios para a loja parceira).

> **👤 Cliente:** Oi! Vocês têm o violão Giannini GF-3D Sunburst em estoque? E aproveitando, quero levar um jogo de cordas de aço, um cabo P10 e um amplificador pequeno.

> **🛠️ Tool Call Executada:**
> `search_products(query="Giannini GF-3D")`
> `handle_out_of_scope_request(item_requested="jogo de cordas de aço, cabo P10 e amplificador")`

> **🎵 Empório da Música:**
> Olá! Tudo ótimo por aqui! Consultei nosso sistema agora mesmo e tenho duas informações importantes para te passar com toda transparência:
>
> ### 1. Sobre o Violão Giannini GF-3D Dreadnought Sunburst
> No momento, o **Giannini GF-3D Sunburst** (R$ 799,90) está **temporariamente sem estoque** (0 unidades disponíveis).
> Porém, se você procura um excelente violão de aço nessa mesma faixa de preço ou formato, temos estas ótimas opções **disponíveis para pronta-entrega**:
> - **Giannini GF-1R Aço Folk Sunburst** — **R$ 579,90** *(ou **R$ 550,91** à vista no PIX)* | Estoque: 7 un. *(Mesma marca e acabamento Sunburst clássico!)*
> - **Tagima Dallas Tuner Aço Natural** — **R$ 749,00** *(ou **R$ 711,55** à vista no PIX)* | Estoque: 9 un. *(Já vem com afinador integrado!)*
> - **Shelby SGD-195E Elétrico Aço Sunburst** — **R$ 799,00** *(ou **R$ 759,05** à vista no PIX)* | Estoque: 6 un. *(Formato Dreadnought em Sunburst e já eletroacústico!)*
> - **Tagima Woodstock Dreadnought Natural** — **R$ 899,00** *(ou **R$ 854,05** à vista no PIX)* | Estoque: 11 un. *(Corpo Dreadnought amplo e som super potente!)*
>
> ### 2. Sobre as Cordas, Cabo P10 e Amplificador
> Aqui na **Empório da Música** nós trabalhamos **exclusivamente com instrumentos musicais** (violões, guitarras, baixos, baterias, teclados, sopros, cordas orquestrais e ukuleles) — por política da loja, **não comercializamos acessórios** como encordoamentos avulsos, cabos, palhetas, cases, pedais ou amplificadores.
>
> Para comprar as cordas, o cabo P10 e o amplificador, recomendamos com carinho a nossa loja parceira aqui em Campo Grande:
> 👉 **Pantanal Music & Acessórios**
> - **Endereço:** Av. Afonso Pena, Centro — Campo Grande/MS
> - **Telefone / WhatsApp:** (67) 3322-1000
>
> Gostaria de conhecer melhor o **Giannini GF-1R Sunburst** ou o **Shelby SGD-195E Sunburst** para substituir o GF-3D? 🎸

