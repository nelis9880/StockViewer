import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.title("Stock Viewer V4.2")
st.write("Een professionele aandelen analyse tool met meerdere secties voor koers, dividend en waardering.")

ticker = st.text_input("Vul een ticker in (bijv. AAPL):")

period = st.selectbox(
    "Kies periode",
    ["1mo", "3mo", "6mo", "1y", "5y"],
    index=3
)

if ticker:
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)

    tab1, tab2, tab3 = st.tabs(["Koers", "Dividend", "Waardering"])

    with tab1:
        st.subheader("Koersontwikkeling")
        if not data.empty:
            current_price = data["Close"].iloc[-1]
            prev_price = data["Close"].iloc[-2] if len(data) > 1 else current_price
            change = current_price - prev_price
            pct_change = (change / prev_price) * 100 if prev_price != 0 else 0

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label=f"Huidige koers ({ticker.upper()})",
                    value=f"${current_price:.2f}",
                    delta=f"{change:.2f} ({pct_change:.2f}%)"
                )

            st.line_chart(data["Close"])
        else:
            st.error("Geen data gevonden.")

    with tab2:
        st.subheader("Dividendgeschiedenis")
        dividends = stock.dividends.loc[data.index.min():] if not data.empty else None

        if dividends is not None and not dividends.empty:
            st.line_chart(dividends)
        else:
            st.write("Geen dividendgegevens beschikbaar.")

    with tab3:
        st.subheader("Fundamentele Waardering (Basisgegevens)")
        info = stock.info
        
        # Benodigde waarderingsdata ophalen
        market_cap = info.get("marketCap")
        revenue = info.get("totalRevenue")
        net_income = info.get("netIncomeToCommon")
        eps = info.get("trailingEps")
        pe = info.get("trailingPE")
        ps = info.get("priceToSalesTrailing12Months")
        div_yield = info.get("dividendYield")
        shares_outstanding = info.get("sharesOutstanding")

        st.markdown("Deze sectie toont de belangrijkste kerncijfers om een bedrijf op hoofdlijnen te waarderen")

        # Twee kolommen voor overzicht
        colA, colB = st.columns(2)

        with colA:
            st.markdown("### Bedrijfswaarde")
            st.write(f"**Market Cap:** {market_cap:,} USD" if market_cap else "Market Cap niet beschikbaar")
            st.write(f"**Omzet (Revenue):** {revenue:,} USD" if revenue else "Omzet niet beschikbaar")
            st.write(f"**Netto Winst:** {net_income:,} USD" if net_income else "Netto winst niet beschikbaar")
            st.write(f"**Aantal aandelen:** {shares_outstanding:,}" if shares_outstanding else "Aantal aandelen niet beschikbaar")

            # Enterprise Value componenten
            cash = info.get("totalCash")
            debt = info.get("totalDebt")

            # Enterprise Value berekenen (alleen tonen als date beschikbaar is)
            if market_cap and (cash is not None or debt is not None):
                if cash is None:
                    cash = 0
                if debt is None:
                    debt = 0

                enterprise_value = market_cap + debt - cash
                st.write(f"**Enterprise Value (EV):** {enterprise_value:,} USD")
                st.write(f"**Cash:** {cash:,} USD")
                st.write(f"**Debt:** {debt:,} USD")
            else:
                st.write("Enterprise Value niet beschikbaar")

        with colB:
            st.markdown("### Ratio's & Rendement")
            st.write(f"**EPS:** {eps:.2f}" if eps else "EPS niet beschikbaar")
            st.write(f"**PE-ratio:** {pe:.2f}" if pe else "PE niet beschikbaar")
            st.write(f"**Price-to-Sales:** {ps:.2f}" if ps else "Price-to-Sales niet beschikbaar")
            st.write(f"**Dividend Yield:** {div_yield * 100:.2f}%" if div_yield else "Dividend Yield niet beschikbaar")

        st.markdown("---")
        st.markdown("### Uitleg (simpel)")
        st.markdown("""
        **Market Cap** – Totale waarde van het bedrijf op de beurs.

        **Revenue (Omzet)** – Hoeveel geld het bedrijf binnenhaalt.

        **Net Income (Netto Winst)** – Winst die overblijft na alle kosten.

        **Aantal aandelen** – Hoeveel aandelen het bedrijf heeft uitgegeven.

        **Cash** – Hoeveel geld het bedrijf direct beschikbaar heeft. Wordt gebruikt in waarderingen omdat bedrijven met veel cash eigenlijk ‘goedkoper’ zijn.

        **Debt (Schulden)** – Totaal bedrag dat het bedrijf nog moet betalen aan leningen.

        **Enterprise Value (EV)** – Echte ‘bedrijfswaarde’.  
        Formule: **EV = Market Cap + Debt – Cash**  
        EV houdt beter rekening met de financiële situatie van een bedrijf dan Market Cap.

        **EPS (Earnings per Share)** – Winst per aandeel.

        **PE-ratio** – Hoeveel beleggers betalen voor €1 winst.

        **Price-to-Sales** – Hoeveel beleggers betalen per euro omzet.

        **Dividend Yield** – Percentage rendement dat je krijgt via dividenduitkering.
        """)