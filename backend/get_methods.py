import pandas as pd
# regasire angajati dintr-un departament
def get_employees_department(id_departament, connection):
        sql_r="""select * from angajati where id_departament=:id_departament"""
        df = pd.read_sql(sql_r, con=connection, params={'id_departament':id_departament})
        df['DATA_ANGAJARE'] = pd.to_datetime(df['DATA_ANGAJARE'], format='%d-%m-%Y')
        return df

# calcul comenzi pentru un angajat
# se apeleaza procedura stocata p_manag_angajati.comenzi_intermediate
def comenzi_angajat(id_angajat, connection):
        cursor = connection.cursor()
        #parametrii de tip OUT
        nr_comenzi = cursor.var(int)
        val_comenzi = cursor.var(float)
        cursor.callproc('p_manag_angajati.comenzi_intermediate', [id_angajat, nr_comenzi, val_comenzi])
        nr_comenzi=nr_comenzi.getvalue()
        val_comenzi=val_comenzi.getvalue()
        cursor.close()
        return nr_comenzi, val_comenzi

# regasire departamente
def get_departments(connection):
        sql_r="""select * from departamente"""
        df = pd.read_sql(sql_r, con=connection)
        return df
# statistici departamente
def statistici_dep(connection, id_departament):
        cursor = connection.cursor()
        #parametrii de tip OUT
        nr_angajati = cursor.var(int)
        venit_mediu = cursor.var(float)
        venit_total = cursor.var(float)
        # apelarea procedurii stocate din pachetul p_manag_angajati
        cursor.callproc('p_manag_angajati.calc_venit_dep', [id_departament, nr_angajati, venit_mediu, venit_total])
        nr_angajati=nr_angajati.getvalue()
        venit_mediu=venit_mediu.getvalue()
        venit_total=venit_total.getvalue()
        cursor.close()
        return nr_angajati, venit_mediu, venit_total
# regasire clienti
def get_clienti(connection):
        sql_r="""select * from V_CLIENTI_COMENZI"""
        df = pd.read_sql(sql_r, con=connection)
        return df