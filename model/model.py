from database.impianto_DAO import ImpiantoDAO
from database.consumo_DAO import ConsumoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        consumo_medio = list()

        for imp in self._impianti:
            consumi = ConsumoDAO.get_consumi(imp.id)
            somma = 0
            contatore = 0

            for c in consumi:
                mese_consumo = c.data.month

                if mese_consumo == mese:
                    somma += c.kwh
                    contatore += 1

            media = somma / contatore
            consumo_medio.append((imp.nome, media))

        return consumo_medio



    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO
        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
               self.__costo_ottimo = costo_corrente
               self.__sequenza_ottima = sequenza_parziale.copy()
            return

        for imp in self._impianti:
            imp_id = imp.id


            consumo_giorno = consumi_settimana[imp_id][giorno-1]

            costo_spostamento = 0
            if ultimo_impianto is not None and ultimo_impianto != imp_id:
                costo_spostamento = 5

            nuovo_costo = costo_corrente + consumo_giorno + costo_spostamento

            sequenza_parziale.append(imp_id)

            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                imp_id,
                nuovo_costo,
                consumi_settimana
            )

            sequenza_parziale.pop()




    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO

        consumi_settimana = dict()

        for impianto in self._impianti:
            consumi = ConsumoDAO.get_consumi(impianto.id)

            lista_giorni = []

            for c in consumi:
                if c.data.month == mese and 1 <= c.data.day <= 7:
                    lista_giorni.append((c.data.day, c.kwh))

            # ordina per giorno
            lista_giorni.sort(key=lambda x: x[0])

            kwh_ordinati = [k for (day, k) in lista_giorni]

            consumi_settimana[impianto.id] = kwh_ordinati

        return consumi_settimana