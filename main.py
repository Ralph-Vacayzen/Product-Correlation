import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title='Product Correlation', page_icon='⚖️', layout="centered", initial_sidebar_state="auto", menu_items=None)

st.caption('VACAYZEN')
st.title('Product Correlation')
st.info('A tool to tell how frequent one product category is rented with all other assets.')

file = st.file_uploader('Rental Agreement Lines (RAL_AssetToRentalAgreement)','csv')

if file is not None:
    st.divider()

    st.toast('Reading uploaded file...')
    df = pd.read_csv(file)

    st.toast('Providing product category options...')
    st.subheader('Product of Interest')
    option = st.selectbox('Product', df.Product.sort_values().unique(),label_visibility='collapsed')

    st.divider()
    
    st.subheader('Area of Interest')
    tab1, tab2 = st.tabs(['Product to Product', 'Product to Partner'])

    with tab1:
        st.subheader('Question')
        st.success('What is rented with **' + option + '**?', icon='🙋🏻‍♂️')
        st.info('What percentage of orders have **' + option + '** assets on them? (See *Proportion*.)',icon='🤏🏼')
        st.info('How often is an order strictly for **' + option + '** assets? (See *Singularity*.)',icon='💯')
        st.info('How often is a non-**' + option + '** asset rented with a **' + option + '** asset? (See *Correlation*.)', icon='🕰️')

        st.divider()

        st.toast('Filtering options...')
        dfo = df[df.Product == option].sort_values(by='Description')
        dfn = df[~(df.Product == option)].sort_values(by='Description')

        st.subheader('Assets of Interest')
        
        oproducts = dfo.Description.unique()
        nproducts = dfn.Description.unique()

        l, r = st.columns(2)
        with l.expander('**' + option + '** Assets'):
            o = pd.DataFrame(oproducts, columns=['Assets']).sort_values(by='Assets').reset_index(drop=True)
            st.dataframe(o, use_container_width=True, hide_index=True)

        with r.expander('Everything Else Assets'):
            n = pd.DataFrame(nproducts, columns=['Assets']).sort_values(by='Assets').reset_index(drop=True)
            st.dataframe(n, use_container_width=True, hide_index=True)

        st.toast('Scanning rental agreements...')
        ordersToAsset   = df.groupby('Description')['RentalAgreementID'].apply(list)
        categoryToOrder = df.groupby('RentalAgreementID')['Product'].apply(set)

        st.divider()

        st.toast('Calculating proportion...')
        orders           = df['RentalAgreementID'].sort_values().unique()
        categoryToOrder  = categoryToOrder.to_frame()
        optionOrders     = dfo['RentalAgreementID'].sort_values().unique()

        st.subheader('Proportion', help='What percentage of orders have the product of interest on them.')

        l, m, r = st.columns(3)

        l.metric('Orders', len(orders))
        m.metric('**' + option + '** Orders', len(optionOrders))
        r.metric('**' + option + '** Ratio', round(len(optionOrders) / len(orders) * 100,2))

        st.divider()

        st.toast('Calculating singularity...')
        optionOnlyOrders = categoryToOrder[categoryToOrder['Product'] == {option}]

        st.subheader('Singularity', help='How often an order is strictly for the product of interest.')

        l, m, r = st.columns(3)

        l.metric('**' + option + '** Orders', len(optionOrders))
        m.metric('Strictly **' + option + '** Orders', len(optionOnlyOrders))
        r.metric('Singularity Ratio', round(len(optionOnlyOrders) / len(optionOrders) * 100,2))

        st.divider()

        st.toast('Calculating correlations...')
        results = [[option,'Asset','Correlation']]

        for optionproduct in oproducts:
            oorders = ordersToAsset[optionproduct]

            for notproduct in nproducts:
                norders = ordersToAsset[notproduct]
                shared  = set(oorders).intersection(norders)
                ratio   = round(len(shared) / len(oorders) * 100, 2)
                results.append([optionproduct,notproduct,ratio])
        
        results = pd.DataFrame(data=results[1:],columns=results[0])

        st.subheader('Correlation', help='How often the product of interest is on the same order as a non-product-of-interest.')
        st.latex(r'''Correlation = \frac{Orders_{assetA} \cap Orders_{assetB}}{Orders_{assetA}}''')
        st.dataframe(results, use_container_width=True, hide_index=True)

        st.subheader('Correlation Drill-in')

        asset = st.selectbox('Asset of Interest', oproducts)

        result = results[results[option] == asset]

        result = result.sort_values(by='Correlation', ascending=False)

        st.dataframe(result, use_container_width=True, hide_index=True)