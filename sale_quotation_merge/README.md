# Sale Quotation Merge (Odoo 20)

Kevyt moduuli useiden tarjousten yhdistämiseen yhdeksi Odoo 20:ssä.

## Toiminnallisuus

Moduuli lisää tarjouslistanäkymään (**Myynti -> Tarjoukset**) toiminnon **"Yhdistä tarjoukset"**:

1. **Valinta listanäkymästä**:
   - Valitse vähintään kaksi saman asiakkaan tarjousta (valintaruuduilla).
   - Valitse yläpalkin valikosta **Toiminto (Action) -> Yhdistä tarjoukset**.

2. **Yhdistämisikkuna (Wizard)**:
   - **Kohdetarjous**: Valitse mihin tarjoukseen rivit liitetään (oletuksena ensimmäinen valittu).
   - **Yhdistä samat tuoterivit**:
     - *Ei valittuna (oletus)*: Kaikki rivit kopioidaan erillisinä kohdetarjoukseen.
     - *Valittuna*: Jos tuote, yksikköhinta, alennus ja verot täsmäävät, rivien määrät (`product_uom_qty`) lasketaan yhteen.
   - **Lähdetarjousten käsittely**:
     - *Peruuta lähdetarjoukset (oletus)*: Asettaa yhdistetyt lähdetarjoukset tilaan Peruttu (`cancel`).
     - *Arkistoi lähdetarjoukset*: Asettaa yhdistetyt lähdetarjoukset ei-aktiivisiksi (`active = False`).
     - *Älä muuta lähdetarjouksia*: Jättää vanhat tarjoukset koskemattomiksi.
   - **Kopioi myös ehdot ja muistiinpanot**:
     - Liittää lähdetarjousten ehdot (`note`) kohdetarjouksen lisätietoihin selkein otsikoin.

3. **Jäljitettävyys**:
   - Kohdetarjouksen ja lähdetarjousten Chatteriin tallennetaan automaattisesti linkit ja merkintä siitä, mitkä tarjoukset yhdistettiin ja milloin.

4. **Tarkistukset**:
   - Kaikkien tarjousten on oltava luonnostilassa (`draft` tai `sent`).
   - Kaikkien tarjousten on kuuluttava samalle asiakkaalle ja yritykselle.
   - Kaikilla tarjouksilla on oltava sama valuutta.

## Asennus / Päivitys

```bash
# Asenna moduuli tietokantaan:
./odoo-bin -i sale_quotation_merge -d <tietokanta>

# Päivitä moduuli muutosten jälkeen:
./odoo-bin -u sale_quotation_merge -d <tietokanta>
```
