import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title='Product Correllation', page_icon='⚖️', layout="centered", initial_sidebar_state="auto", menu_items=None)

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

    st.toast('Filtering options...')
    dfo = df[df.Product == option].sort_values(by='Description')
    dfn = df[~(df.Product == option)].sort_values(by='Description')

    st.subheader('Product Categories')
    
    oproducts = dfo.Description.unique()
    nproducts = dfn.Description.unique()

    l, r = st.columns(2)
    with l.expander('**' + option + '** Assets'):
        o = pd.DataFrame(oproducts, columns=['Assets']).sort_values(by='Assets').reset_index(drop=True)
        st.dataframe(o, use_container_width=True, hide_index=True)

    with r.expander('Everything Else Assets'):
        n = pd.DataFrame(nproducts, columns=['Assets']).sort_values(by='Assets').reset_index(drop=True)
        st.dataframe(n, use_container_width=True, hide_index=True)

    st.subheader('Question')
    st.success('What is rented with **' + option + '**?')
    st.info('How often is a non-**' + option + '** asset rented with a **' + option + '** asset?')

    st.toast('Scanning rental agreements...')
    ordersToAsset = df.groupby('Description')['RentalAgreementID'].apply(list)

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

    st.subheader('Correlation')
    st.latex(r'''Correlation = \frac{Orders_{assetA} \cap Orders_{assetB}}{Orders_{assetA}}''')
    st.dataframe(results, use_container_width=True, hide_index=True)

    st.subheader('Scrutinization')

    asset = st.selectbox('Asset of Interest', oproducts)

    result = results[results[option] == asset]

    result = result.sort_values(by='Correlation', ascending=False)

    st.dataframe(result, use_container_width=True, hide_index=True)

