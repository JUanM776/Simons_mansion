# ═══════════════════════════════════════════════════════════════════
#  LA MANSIÓN DE SIMÓN
#  Una historia de secretos, silencios y supervivencia
# ═══════════════════════════════════════════════════════════════════

import os, time, sys, textwrap, random

# ── Configuración visual ──────────────────────────────────────────

W = 66
VELOCIDAD = 0.018
VELOCIDAD_LENTA = 0.028

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

def _wrap(texto, indent=2):
    lineas = textwrap.wrap(texto, W - indent)
    return [" " * indent + l for l in lineas]

def escribir(texto, vel=VELOCIDAD):
    for linea in _wrap(texto):
        for c in linea:
            sys.stdout.write(c); sys.stdout.flush(); time.sleep(vel)
        print()
    print()

def escribir_lento(texto):
    escribir(texto, VELOCIDAD_LENTA)

def narrar(texto):
    """Texto narrativo con sangría y ritmo."""
    for linea in _wrap(texto, 4):
        print(linea)
    print()

def dialogo(nombre, texto, pausa_final=True):
    prefijo = f"  {nombre.upper()}: "
    sys.stdout.write(prefijo)
    envuelto = textwrap.wrap(texto, W - len(prefijo))
    for i, linea in enumerate(envuelto):
        if i > 0:
            sys.stdout.write(" " * len(prefijo))
        for c in linea:
            sys.stdout.write(c); sys.stdout.flush(); time.sleep(0.015)
        print()
    if pausa_final:
        print()

def acotacion(texto):
    """Texto entre paréntesis, más sutil."""
    for linea in _wrap(texto, 6):
        print(f"\033[2m{linea}\033[0m")
    print()

def separador():
    print(f"\n  {'─' * (W - 4)}\n")

def pausa(msg=None):
    if msg:
        print(f"  {msg}")
    input(f"\n  {'▸ Presiona ENTER para continuar...':^{W}}\n")

def titulo(texto, sub=""):
    limpiar()
    print()
    print(f"  {'═' * (W - 4)}")
    print(f"{texto:^{W}}")
    if sub:
        print(f"\033[2m{sub:^{W}}\033[0m")
    print(f"  {'═' * (W - 4)}")
    print()

def elegir(opciones):
    print()
    for i, op in enumerate(opciones, 1):
        print(f"    [{i}] {op}")
    print()
    while True:
        try:
            r = input("    ▸ ").strip()
            e = int(r)
            if 1 <= e <= len(opciones):
                print()
                return e
        except (ValueError, EOFError):
            pass
        print("    Opción inválida. Intenta de nuevo.")

# ── Estado del juego ──────────────────────────────────────────────

class Personaje:
    def __init__(self, nombre, rol, edad, ocupacion, secreto, objeto, ubicacion_obj):
        self.nombre = nombre
        self.rol = rol
        self.edad = edad
        self.ocupacion = ocupacion
        self.secreto = secreto
        self.objeto = objeto
        self.ubicacion_obj = ubicacion_obj
        self.aislamiento = 0
        self.presente = True
        self.interactuado_cap = False
        self.objeto_encontrado = False
        self.confianza = 0  # -100 a 100

    def aislar(self, n):
        if self.presente:
            self.aislamiento = min(100, self.aislamiento + n)

    def conectar(self, n):
        if self.presente:
            self.aislamiento = max(0, self.aislamiento - n)
            self.confianza = min(100, self.confianza + n)
            self.interactuado_cap = True

    def barra(self):
        lleno = self.aislamiento // 10
        vacio = 10 - lleno
        if self.aislamiento >= 75:
            tag = "⚠ CRÍTICO"
        elif self.aislamiento >= 50:
            tag = "▲ alto"
        elif self.aislamiento >= 25:
            tag = "~ medio"
        else:
            tag = "✓ estable"
        return f"{'█' * lleno}{'░' * vacio} {self.aislamiento:3d}  {tag}"


class Estado:
    def __init__(self):
        self.personajes = {}
        self.pistas = set()
        self.decisiones = []
        self.capitulo = 0
        self.simon_encontrado = False
        self.codigo_encontrado = False
        self._crear_personajes()

    def _crear_personajes(self):
        datos = [
            ("Ben", "El Dinero", 38, "Corredor de bolsa en quiebra",
             "Desvió fondos de las ventas de Simón durante años",
             "Libro de cuentas comprometedor", "Habitación de Simón"),
            ("Lisa", "La Evidencia", 31, "Periodista suspendida",
             "Tiene copias de pruebas de un crimen que Simón presenció",
             "Carpeta con fotografías y documentos", "Galería"),
            ("Robert", "La Carta", 54, "Abogado notarial semi-retirado",
             "Es hermano secreto de Simón por parte de padre",
             "Carta manuscrita del padre común", "Lobby"),
            ("Ana", "Las Joyas", 45, "Galerista y tasadora de arte",
             "Usó joyas familiares de Simón como garantía sin permiso",
             "Estuche de cuero con joyas familiares", "Estudio"),
            ("Lucas", "El Relicario", 27, "Estudiante, ex-ayudante de Simón",
             "Tomó un relicario de plata que pertenecía a Simón",
             "Relicario de plata con inscripción", "Sala de cámaras"),
        ]
        for d in datos:
            p = Personaje(*d)
            self.personajes[d[0]] = p

    def presentes(self):
        return [n for n, p in self.personajes.items() if p.presente]

    def p(self, nombre):
        return self.personajes[nombre]

    def tiene(self, pista):
        return pista in self.pistas

    def guardar_pista(self, pista):
        self.pistas.add(pista)

    def decidir(self, desc):
        self.decisiones.append(desc)

    def fin_capitulo(self):
        """Aplica mecánica de aislamiento al final de cada capítulo."""
        for p in self.personajes.values():
            if p.presente and not p.interactuado_cap:
                p.aislar(25)
        todos = all(p.presente for p in self.personajes.values())
        if todos:
            for p in self.personajes.values():
                p.conectar(5)
        for p in self.personajes.values():
            p.interactuado_cap = False

    def verificar_abandonos(self):
        candidatos = [(n, p.aislamiento) for n, p in self.personajes.items()
                      if p.presente and p.aislamiento >= 75]
        if not candidatos:
            return None
        candidatos.sort(key=lambda x: -x[1])
        nombre = candidatos[0][0]
        self.personajes[nombre].presente = False
        return nombre

    def mostrar_grupo(self):
        separador()
        print("  ESTADO DEL GRUPO")
        print()
        for nombre, p in self.personajes.items():
            if p.presente:
                print(f"    {nombre:8s}  {p.barra()}")
            else:
                print(f"    {nombre:8s}  ──────────  ABANDONÓ LA MANSIÓN")
        separador()


G = Estado()

# ══════════════════════════════════════════════════════════════
#  PRÓLOGO
# ══════════════════════════════════════════════════════════════

def prologo():
    limpiar()
    print("\n" * 3)
    time.sleep(0.5)
    print(f"{'L A   M A N S I Ó N   D E   S I M Ó N':^{W}}")
    time.sleep(1)
    print(f"\033[2m{'Una historia de secretos, silencios y supervivencia':^{W}}\033[0m")
    time.sleep(2)
    print("\n" * 2)
    pausa()

    titulo("P R E M I S A")
    escribir_lento("Son las tres de la tarde.")
    time.sleep(0.5)
    narrar("Una mansión antigua, de paredes que huelen a barniz viejo "
           "y a secretos acumulados durante décadas, recibe a cinco "
           "desconocidos que, sin embargo, no lo son del todo entre sí.")
    narrar("Los une un nombre: Simón. Un pintor. Un hombre que, según "
           "les comunicaron hace pocos días, ha muerto.")
    pausa()

    narrar("Pero cada uno llegó con algo más que condolencias. Cada uno "
           "llegó con una razón propia, silenciosa, que no piensa "
           "compartir con nadie. Y todos, sin excepción, buscan algo "
           "dentro de esa mansión.")
    narrar("Lo que ninguno sabe es que no están solos. En algún rincón "
           "de la casa, alguien más aguarda. Alguien cuya razón para "
           "estar ahí es mucho más oscura que todas las demás juntas.")
    print()
    escribir_lento("El jugador observa. El jugador explora.")
    escribir_lento("El jugador decide quién sobrevive.")
    pausa()

    # Presentación de personajes
    titulo("L O S   P E R S O N A J E S")
    for nombre, p in G.personajes.items():
        print(f"  ◆ {nombre.upper()} — {p.rol}")
        print(f"    {p.edad} años. {p.ocupacion}.")
        acotacion(p.secreto + ".")
    narrar("Y en algún lugar de la mansión, oculto, retenido, esperando: "
           "Simón. El pintor. El hombre que todos creen muerto.")
    pausa()

    titulo("M E C Á N I C A   D E   J U E G O")
    narrar("No es el asesino lo que mata a los personajes. Es la soledad.")
    narrar("Cada personaje tiene un nivel de aislamiento. Si lo ignoras, "
           "crece. Si hablas con ellos, baja. Si el aislamiento de alguien "
           "supera el umbral crítico al final de un capítulo, esa persona "
           "abandonará la mansión para siempre.")
    narrar("Tus decisiones determinan quién sobrevive, qué pistas "
           "descubres, y cómo termina esta historia.")
    narrar("Explora cada escenario. Habla con todos. Encuentra a Simón "
           "antes de que sea demasiado tarde.")
    pausa()

# ══════════════════════════════════════════════════════════════
#  CAPÍTULO 1 — LA LLEGADA (3:00 PM)
# ══════════════════════════════════════════════════════════════

def capitulo_1():
    G.capitulo = 1
    titulo("C A P Í T U L O   1", "La Llegada — 3:00 PM")
    time.sleep(0.5)

    narrar("El primero en llegar fue Robert. Lo hizo con diez minutos de "
           "adelanto, como hacía siempre, como si la puntualidad fuera una "
           "forma de demostrar que tenía el control de algo.")
    narrar("El lobby olía a polvo y a rosas secas. Techos altos con molduras "
           "de yeso amarillento, una escalera central de madera oscura, "
           "sillones de cuero rojo envejecido, una chimenea apagada.")
    pausa()

    narrar("Ana llegó a las tres en punto. Entró con la seguridad de quien "
           "conoce los espacios de arte. Saludó a Robert con una inclinación "
           "de cabeza, sin sonreír. Ninguno preguntó qué hacía el otro allí.")
    narrar("Ben llegó tres minutos después, con la corbata aflojada y una "
           "expresión de alguien que lleva semanas sin dormir bien. "
           "Lanzó un 'buenas tardes' demasiado animado que no convenció a nadie.")
    narrar("Lucas fue el cuarto. Llegó con una mochila al hombro y los "
           "auriculares colgando del cuello. Cuando vio a los otros tres, "
           "se detuvo un momento, sorprendido de no ser el único.")
    narrar("Lisa llegó la última, a las tres y cuarto. Entró mirando cada "
           "detalle del espacio con ojos profesionales. Eligió el sillón "
           "más cercano a la puerta de entrada.")
    narrar("Durante unos minutos nadie habló. Luego fue Ben quien rompió "
           "el silencio con un comentario sobre el clima. El grupo empezó, "
           "lentamente, a intercambiar palabras que no decían nada real.")
    pausa()

    # ── Exploración del Lobby ──
    explorar_lobby()

    # ── Interacciones ──
    titulo("E L   L O B B Y", "Interacciones — Capítulo 1")
    narrar("Los cinco están dispersos por el lobby. Puedes hablar con "
           "quien quieras. Cada conversación importa.")
    interacciones_c1()

    # ── Decisión ──
    titulo("D E C I S I Ó N", "Capítulo 1")
    narrar("Llevan una hora en el lobby. La tensión es palpable. "
           "Nadie ha dicho por qué está realmente aquí. "
           "El silencio empieza a pesar.")
    e = elegir([
        "Proponer explorar la mansión juntos, como grupo",
        "Sugerir que cada uno explore por su cuenta",
        "Intentar que el grupo hable abiertamente sobre Simón",
    ])
    if e == 1:
        G.decidir("grupo_unido_c1")
        narrar("El grupo acepta, aunque con reservas. Hay algo reconfortante "
               "en moverse juntos por una casa que ninguno conoce del todo. "
               "Los pasos de cinco personas suenan distintos a los de una sola.")
        for n in G.presentes(): G.p(n).conectar(10)
    elif e == 2:
        G.decidir("separados_c1")
        narrar("Cada uno toma una dirección distinta. La mansión los absorbe "
               "en silencio. La distancia entre ellos crece con cada paso. "
               "Desde algún lugar de la casa, alguien observa cómo se separan.")
        for n in G.presentes(): G.p(n).aislar(15)
    else:
        G.decidir("hablar_c1")
        narrar("Las respuestas son vagas, calculadas. Pero en los silencios "
               "entre las palabras hay más información que en las palabras mismas. "
               "Algo se mueve debajo de la superficie de cada frase.")
        for n in G.presentes(): G.p(n).conectar(5)

    _cierre_capitulo()


def explorar_lobby():
    titulo("E L   L O B B Y", "Exploración libre")
    narrar("La luz entra por ventanas emplomadas que filtran el sol de la "
           "tarde en franjas anaranjadas. Hay flores secas en un jarrón "
           "sobre la repisa. Un abrigo cuelga del perchero cerca de la puerta.")
    visto = set()
    while True:
        ops = []
        if "libro" not in visto:
            ops.append("Examinar el libro de visitas sobre la mesita")
        if "abrigo" not in visto:
            ops.append("Revisar el abrigo en el perchero")
        if "foto" not in visto:
            ops.append("Mirar la fotografía sobre la chimenea")
        if "periodico" not in visto:
            ops.append("Leer el periódico doblado en el sillón")
        ops.append("Terminar de explorar")
        e = elegir(ops)
        sel = ops[e - 1]

        if "libro de visitas" in sel:
            visto.add("libro")
            narrar("Sobre la mesita de entrada hay un libro donde los visitantes "
                   "de la mansión firmaban su llegada. Las últimas tres entradas "
                   "son de los últimos seis meses.")
            narrar("Una de ellas está tachada con tinta roja. El nombre debajo "
                   "de la tachadura es ilegible, pero la fecha es de hace "
                   "exactamente tres semanas.")
            G.guardar_pista("entrada_tachada")

        elif "abrigo" in sel:
            visto.add("abrigo")
            narrar("Un abrigo de hombre de talla grande. En el bolsillo interior "
                   "hay una nota manuscrita, sin firma:")
            dialogo("NOTA", "No confíes en nadie que llegue antes que tú.")
            acotacion("La letra es firme, decidida. No es la letra de alguien "
                      "que escribe con miedo. Es la de alguien que advierte.")
            G.guardar_pista("nota_abrigo")

        elif "fotografía" in sel:
            visto.add("foto")
            narrar("Una fotografía en blanco y negro de Simón joven, junto a un "
                   "hombre mayor de rasgos severos. Al dorso, escrito a lápiz:")
            dialogo("DORSO", "Padre e hijo. 1987.")
            acotacion("Robert, al otro lado de la sala, desvía la mirada "
                      "cuando notas que examinas la fotografía.")
            G.guardar_pista("foto_padre_hijo")
            G.p("Robert").aislar(10)

        elif "periódico" in sel:
            visto.add("periodico")
            narrar("Un periódico local de hace tres días. La esquina de la "
                   "página de sucesos está doblada. El titular visible dice:")
            dialogo("TITULAR", "Incendio en almacén del puerto, investigación reabierta.")
            acotacion("Lisa, desde su sillón, mira el periódico con una "
                      "expresión que intenta ser indiferente y no lo consigue.")
            G.guardar_pista("incendio_periodico")
            G.p("Lisa").conectar(10)

        else:
            break


def interacciones_c1():
    hablados = set()
    while True:
        vivos = [n for n in G.presentes() if n not in hablados]
        if not vivos:
            narrar("Ya hablaste con todos los presentes.")
            break
        ops = [f"Hablar con {n} — {G.p(n).rol}" for n in vivos]
        ops.append("No hablar con nadie más")
        e = elegir(ops)
        if e > len(vivos):
            break
        nombre = vivos[e - 1]
        hablados.add(nombre)
        G.p(nombre).conectar(20)
        _dialogo_c1(nombre)


def _dialogo_c1(nombre):
    separador()
    if nombre == "Robert":
        dialogo("ROBERT", "Vine porque me lo pidieron. Un abogado, no sé "
                "quién lo contrató, me envió una carta diciéndome que había "
                "asuntos pendientes relacionados con la herencia de Simón "
                "que requerían mi presencia.")
        acotacion("Hace una pausa. Su postura es rígida, ensayada.")
        dialogo("ROBERT", "No lo conocía bien. Nos cruzamos en algunos "
                "círculos. Nada más.", False)
        acotacion("Lo dice con demasiada calma. La clase de calma que se ensaya "
                  "frente al espejo antes de salir de casa.")

    elif nombre == "Ana":
        dialogo("ANA", "Era mi cliente. Uno de los mejores que he tenido, "
                "honestamente. Cuando me dijeron que había muerto...")
        acotacion("Deja la frase en el aire.")
        dialogo("ANA", "Supongo que vine por respeto. Y porque alguien tiene "
                "que asegurarse de que su obra quede bien catalogada. "
                "No es una colección menor.", False)
        acotacion("Sonríe brevemente. Sus ojos recorren la sala como "
                  "tasando cada objeto visible.")

    elif nombre == "Ben":
        dialogo("BEN", "Simón y yo éramos socios, de cierta forma. Él pintaba, "
                "yo me encargaba del lado financiero. Muy informal, ya sabe. "
                "Sin contratos de por medio. La gente creativa suele preferirlo así.")
        acotacion("Saca el teléfono, lo mira, lo guarda.")
        dialogo("BEN", "La verdad es que me enteré de su muerte y quise "
                "venir a... no sé, despedirme. Algo así.", False)
        acotacion("Hay algo en su voz que no alcanza a esconder. "
                  "Urgencia disfrazada de nostalgia.")

    elif nombre == "Lisa":
        dialogo("LISA", "Lo conocí en una exposición. Hace tres años, creo. "
                "Éramos amigos. Buenos amigos.")
        acotacion("Mira hacia la escalera.")
        dialogo("LISA", "¿Alguien sabe qué pasó exactamente? La noticia fue "
                "muy vaga. Muerte repentina, dicen. Pero eso no significa nada.", False)
        acotacion("Lo dice como quien ya tiene una teoría y busca "
                  "que alguien la confirme sin saberlo.")

    elif nombre == "Lucas":
        dialogo("LUCAS", "Yo trabajé para él. Ayudante de estudio, básicamente. "
                "Limpiaba pinceles, preparaba lienzos, a veces mezclaba pigmentos.")
        acotacion("Una pausa.")
        dialogo("LUCAS", "Era muy exigente. Pero aprendí más con él que en "
                "tres años de facultad. No sé por qué vine. Supongo que quería "
                "ver el lugar una última vez.", False)
        acotacion("Lo dice mirando al suelo. Algo en su postura sugiere "
                  "que hay mucho más detrás de esas palabras.")
    pausa()

# ══════════════════════════════════════════════════════════════
#  CAPÍTULO 2 — LA PRIMERA HORA (4:00 PM)
# ══════════════════════════════════════════════════════════════

def capitulo_2():
    G.capitulo = 2
    titulo("C A P Í T U L O   2", "La Primera Hora — 4:00 PM")
    time.sleep(0.5)

    narrar("La luz había cambiado. El sol de la tarde se había movido y "
           "ahora entraba por el lado opuesto, proyectando sombras más "
           "largas sobre el suelo de madera del lobby.")
    narrar("Fue Ana quien descubrió que la puerta del estudio no estaba "
           "cerrada con llave. La empujó sin pensar demasiado y la encontró "
           "abierta. Nadie protestó cuando el grupo comenzó a explorar.")
    pausa()

    explorar_estudio()
    interacciones_c2()

    titulo("D E C I S I Ó N", "Capítulo 2")
    narrar("Ben está nervioso. Sus ojos vuelven una y otra vez al libro "
           "de contabilidad. Lisa mira la fotografía del corcho con una "
           "expresión que mezcla reconocimiento y miedo.")
    e = elegir([
        "Confrontar a Ben sobre las entradas marcadas con B roja",
        "Preguntarle a Lisa quién cree que es la persona de la cinta negra",
        "Proponer subir al segundo piso juntos",
    ])
    if e == 1:
        G.decidir("confrontar_ben_c2")
        narrar("Ben se pone rígido. Tarda un segundo demasiado largo.")
        dialogo("BEN", "Simón y yo teníamos un acuerdo informal. Esas entradas "
                "son transacciones normales. No sé por qué están marcadas así.")
        acotacion("Nadie le cree. Pero nadie lo dice en voz alta. "
                  "El silencio que sigue es más elocuente que cualquier acusación.")
        G.p("Ben").aislar(15)
        G.guardar_pista("ben_confrontado")
    elif e == 2:
        G.decidir("preguntar_lisa_c2")
        acotacion("Lisa baja la voz y mira hacia la puerta.")
        dialogo("LISA", "Simón me habló una vez de alguien. Alguien que sabía "
                "cosas que no debía saber sobre cierto asunto. Me dijo que era "
                "peligroso. No me dijo el nombre.")
        acotacion("Hay algo en la forma en que lo dice que sugiere que Lisa "
                  "sabe más de lo que comparte. Pero al menos está hablando.")
        G.p("Lisa").conectar(20)
        G.guardar_pista("lisa_confia")
    else:
        G.decidir("subir_juntos_c2")
        narrar("El grupo sube en silencio. La escalera cruje bajo sus pasos. "
               "El piso superior pertenece a un territorio más íntimo, más "
               "personal. Nadie había querido ir arriba todavía.")
        for n in G.presentes(): G.p(n).conectar(5)

    _cierre_capitulo()


def explorar_estudio():
    titulo("E L   E S T U D I O   D E   S I M Ó N", "Exploración libre")
    narrar("Escritorio de madera maciza cubierto de papeles, libros apilados "
           "sin orden aparente, una lámpara de pantalla verde, un archivador "
           "metálico con tres cajones. Huele a café frío y a papel húmedo.")
    visto = set()
    while True:
        ops = []
        if "agenda" not in visto:
            ops.append("Examinar la agenda de escritorio")
        if "contabilidad" not in visto:
            ops.append("Revisar el libro de contabilidad abierto")
        if "nota" not in visto:
            ops.append("Leer la nota adhesiva en el monitor")
        if "corcho" not in visto:
            ops.append("Estudiar el tablero de corcho con fotografías")
        if "archivador" not in visto:
            ops.append("Intentar abrir el archivador (cajón superior cerrado)")
        ops.append("Terminar de explorar")
        e = elegir(ops)
        sel = ops[e - 1]

        if "agenda" in sel:
            visto.add("agenda")
            narrar("La agenda del año en curso está abierta en el mes actual. "
                   "Varios días tienen entradas crípticas: nombres de personas "
                   "y horas. El último día registrado, tres días atrás, dice:")
            dialogo("AGENDA", "Reunión cancelada. Peligro.")
            acotacion("Tres días. Simón escribió esto tres días antes de que "
                      "todos recibieran la noticia de su muerte.")
            G.guardar_pista("agenda_peligro")

        elif "contabilidad" in sel:
            visto.add("contabilidad")
            narrar("Un libro de registros con columnas de fechas y montos. "
                   "Los últimos registros muestran discrepancias significativas "
                   "en los ingresos de ventas de los últimos cinco años. "
                   "Hay entradas marcadas con una B roja.")
            acotacion("B de Ben. Las cifras no mienten, aunque las personas sí.")
            G.guardar_pista("libro_contabilidad")
            G.p("Ben").aislar(10)

        elif "nota" in sel:
            visto.add("nota")
            narrar("Una nota amarilla pegada al monitor apagado:")
            dialogo("NOTA", "Copia de seguridad hecha. Ellos no saben que "
                    "tengo el segundo juego.")
            acotacion("Sin contexto adicional. Pero la palabra 'ellos' "
                      "implica que Simón sabía que alguien lo vigilaba.")
            G.guardar_pista("segunda_copia")

        elif "corcho" in sel:
            visto.add("corcho")
            narrar("Un tablero de corcho con fotografías de personas. Cinco "
                   "de ellas tienen nombres escritos debajo: Ben, Lisa, Robert, "
                   "Ana, Lucas. Una sexta fotografía, en el centro, muestra a "
                   "una persona cuyo rostro ha sido cubierto con cinta negra.")
            acotacion("Simón los conocía a todos. Los tenía identificados. "
                      "Y a alguien más, alguien cuyo rostro decidió ocultar.")
            G.guardar_pista("foto_cinta_negra")

        elif "archivador" in sel:
            visto.add("archivador")
            narrar("El cajón superior está cerrado con llave. A través de la "
                   "ranura se puede ver el borde de una carpeta de cuero marrón.")
            acotacion("Necesitarás una llave para abrirlo. Quizás haya una "
                      "en algún otro lugar de la mansión.")
            G.guardar_pista("archivador_cerrado")
        else:
            break


def interacciones_c2():
    titulo("E L   E S T U D I O", "Interacciones — Capítulo 2")
    hablados = set()
    while True:
        vivos = [n for n in G.presentes() if n not in hablados]
        if not vivos:
            narrar("Ya hablaste con todos.")
            break
        ops = [f"Hablar con {n}" for n in vivos] + ["No hablar con nadie más"]
        e = elegir(ops)
        if e > len(vivos): break
        nombre = vivos[e - 1]
        hablados.add(nombre)
        G.p(nombre).conectar(20)
        _dialogo_c2(nombre)


def _dialogo_c2(nombre):
    separador()
    if nombre == "Robert":
        dialogo("ROBERT", "Hay algo perturbador en este cuarto. El hecho de "
                "que todo esté en orden, ¿no le parece? Si alguien muere de "
                "repente, se esperaría cierto caos. Pero aquí todo está "
                "colocado con cuidado.")
        acotacion("Examina los lomos de los libros sin tocarlos.")
        dialogo("ROBERT", "Como si hubiera tenido tiempo de ordenarlo "
                "antes de irse.", False)

    elif nombre == "Ana":
        dialogo("ANA", "Ese libro de registros. Simón nunca llevó sus propias "
                "cuentas. Era una de las cosas que siempre me dijo, que los "
                "números lo aburrían. Que para eso estaban los que entendían "
                "de negocios.")
        acotacion("Sus ojos se detienen un momento en las letras B rojas.")
        dialogo("ANA", "Interesante que tenga esto aquí.", False)

    elif nombre == "Ben":
        acotacion("Ben está de espaldas cuando te acercas. Cuando se gira, "
                  "hay algo en su expresión que no alcanza a esconder.")
        dialogo("BEN", "Estaba mirando los bocetos. Simón tenía un talento "
                "brutal para el retrato, ¿verdad? Lo que me pregunto es quién "
                "tiene acceso a sus papeles ahora que no está. ¿Un abogado? "
                "¿La familia?")
        acotacion("Hay urgencia en su voz, aunque intenta que suene "
                  "como curiosidad.")

    elif nombre == "Lisa":
        acotacion("Lisa baja la voz.")
        dialogo("LISA", "Esa fotografía en el corcho. La de la cinta negra. "
                "Yo sé quién podría ser. O al menos tengo una idea.")
        acotacion("Mira hacia la puerta para asegurarse de que nadie escucha.")
        dialogo("LISA", "Simón me habló una vez de alguien. Alguien que sabía "
                "cosas que no debía saber sobre cierto asunto. Me dijo que era "
                "peligroso. No me dijo el nombre.", False)

    elif nombre == "Lucas":
        acotacion("Está mirando los bocetos con una intensidad que va más "
                  "allá de la admiración artística.")
        dialogo("LUCAS", "Este boceto es mío. Me lo hizo sin que yo lo supiera. "
                "Un día lo vi aquí colgado y se lo mencioné.")
        dialogo("LUCAS", "Me dijo que los mejores retratos se hacen cuando "
                "el sujeto no sabe que lo están mirando.", False)
    pausa()

# ══════════════════════════════════════════════════════════════
#  CAPÍTULO 3 — LA TARDE SILENCIOSA (5:00 PM)
# ══════════════════════════════════════════════════════════════

def capitulo_3():
    G.capitulo = 3
    titulo("C A P Í T U L O   3", "La Tarde Silenciosa — 5:00 PM")
    time.sleep(0.5)

    narrar("Nadie había querido ir arriba todavía. Como si hubiera un "
           "acuerdo tácito de que el piso superior pertenecía a un "
           "territorio distinto, más personal, más íntimo.")
    narrar("La puerta del pasillo del segundo piso estaba abierta, y al "
           "final del corredor, la habitación principal no tenía llave.")
    pausa()

    explorar_habitacion()
    interacciones_c3()

    titulo("D E C I S I Ó N", "Capítulo 3")
    narrar("La carta inconclusa sigue en el suelo. 'No estoy muerto. "
           "Estoy en...' Si Simón está vivo, está en algún lugar de esta "
           "mansión. Y alguien lo puso ahí.")
    e = elegir([
        "Mostrar la carta al grupo y proponer buscar a Simón ahora mismo",
        "Guardar la carta y seguir recopilando información antes de actuar",
        "Preguntarle a Robert directamente sobre su relación con Simón",
    ])
    if e == 1:
        G.decidir("revelar_carta_c3")
        narrar("El grupo reacciona con una mezcla de alivio y alarma. "
               "Lisa dice 'No está muerto' en voz muy baja, como si "
               "necesitara escucharse a sí misma decirlo para creerlo.")
        narrar("Si Simón está vivo, todo cambia. La urgencia une al grupo "
               "de una forma que las palabras no habían logrado.")
        for n in G.presentes(): G.p(n).conectar(15)
        G.guardar_pista("grupo_sabe_simon_vivo")
    elif e == 2:
        G.decidir("guardar_carta_c3")
        narrar("Guardas la carta en tu bolsillo. La información es poder, "
               "pero el tiempo que pasa es tiempo que Simón no tiene. "
               "Cada minuto de silencio es un minuto que alguien más "
               "puede usar para cubrir sus huellas.")
        G.guardar_pista("carta_guardada")
    else:
        G.decidir("confrontar_robert_c3")
        acotacion("Robert se queda en el umbral. Sus nudillos están blancos "
                  "en el marco de la puerta. No entra a la habitación.")
        dialogo("ROBERT", "Simón y yo... nuestra relación era complicada. "
                "Más de lo que nadie sabe. Y ahora que veo este lugar...")
        acotacion("No termina la frase. Baja la mirada hacia el suelo.")
        dialogo("ROBERT", "Ojalá hubiera sido diferente. Eso es todo lo "
                "que puedo decir.", False)
        G.p("Robert").conectar(20)
        G.guardar_pista("robert_relacion_complicada")

    _cierre_capitulo()


def explorar_habitacion():
    titulo("H A B I T A C I Ó N   D E   S I M Ó N", "Exploración libre")
    narrar("Una cama de madera tallada sin hacer, ropa doblada sobre una "
           "silla, una mesita de noche con un vaso de agua a medio beber "
           "todavía fresco. Hay un armario de espejo cuya puerta está "
           "entreabierta.")
    visto = set()
    while True:
        ops = []
        if "vaso" not in visto:
            ops.append("Examinar el vaso de agua en la mesita")
        if "mapa" not in visto:
            ops.append("Estudiar el mapa dibujado a mano en la pared")
        if "carta" not in visto:
            ops.append("Leer la carta a medio escribir en el suelo")
        if "cajon" not in visto:
            ops.append("Abrir el cajón de la mesita de noche")
        if "cama" not in visto:
            ops.append("Mirar bajo la cama")
        ops.append("Terminar de explorar")
        e = elegir(ops)
        sel = ops[e - 1]

        if "vaso" in sel:
            visto.add("vaso")
            narrar("El vaso tiene condensación fresca en el exterior. El agua "
                   "no ha tenido tiempo de evaporarse ni de calentarse.")
            escribir_lento("Simón estuvo aquí hace muy poco.")
            G.guardar_pista("vaso_condensacion")

        elif "mapa" in sel:
            visto.add("mapa")
            narrar("El plano de la mansión muestra todas las habitaciones. "
                   "Cuatro de ellas tienen una cruz al lado. Una quinta "
                   "habitación, en el ala norte, tiene un círculo con signo "
                   "de interrogación.")
            acotacion("El ala norte. Algo hay en el ala norte que Simón "
                      "marcó de forma diferente al resto.")
            G.guardar_pista("mapa_ala_norte")

        elif "carta" in sel:
            visto.add("carta")
            narrar("Una carta a medio escribir, sin destinatario. La pluma "
                   "está tirada en el suelo junto a la silla, como si alguien "
                   "la hubiera soltado con prisa. Dice:")
            dialogo("CARTA", "Si alguien lee esto, no estoy muerto. Estoy en...")
            narrar("La frase se corta. La frase inconclusa pesa en el cuarto "
                   "como una presencia física.")
            G.guardar_pista("simon_vivo")

        elif "cajón" in sel:
            visto.add("cajon")
            narrar("Dentro hay un frasco de pastillas con nombre de medicamento "
                   "para la ansiedad, una fotografía de un niño pequeño con el "
                   "nombre 'Lucas' escrito al dorso, y una llave pequeña sin "
                   "identificar.")
            acotacion("La fotografía del niño. El nombre Lucas. "
                      "¿Quién era ese niño para Simón?")
            G.guardar_pista("foto_nino_lucas")
            G.guardar_pista("llave_pequena")

        elif "cama" in sel:
            visto.add("cama")
            narrar("Un sobre de papel manila con los bordes quemados "
                   "parcialmente. Dentro hay una lista de nombres —ninguno "
                   "de los visitantes— junto a cifras y fechas. Al pie, "
                   "en letras mayúsculas:")
            dialogo("SOBRE", "TESTIGO.")
            acotacion("Simón fue testigo de algo. Y alguien intentó "
                      "quemar la evidencia sin lograrlo del todo.")
            G.guardar_pista("sobre_testigo")
        else:
            break


def interacciones_c3():
    titulo("H A B I T A C I Ó N", "Interacciones — Capítulo 3")
    hablados = set()
    while True:
        vivos = [n for n in G.presentes() if n not in hablados]
        if not vivos: break
        ops = [f"Hablar con {n}" for n in vivos] + ["No hablar con nadie más"]
        e = elegir(ops)
        if e > len(vivos): break
        nombre = vivos[e - 1]
        hablados.add(nombre)
        G.p(nombre).conectar(20)
        _dialogo_c3(nombre)


def _dialogo_c3(nombre):
    separador()
    if nombre == "Ben":
        acotacion("Ben tiene algo en las manos. Lo cierra de golpe, "
                  "demasiado rápido, cuando te acercas.")
        dialogo("BEN", "Estaba buscando algo que explicara qué pasó. "
                "Ya sabes, la agenda decía...")
        acotacion("Se interrumpe.")
        dialogo("BEN", "Mira, este cuarto me pone nervioso. El vaso de agua "
                "todavía tiene condensación. Eso significa...")
        acotacion("No termina. Deja lo que tenía sobre la cama con "
                  "cuidado excesivo.")
        dialogo("BEN", "¿Crees que sigue aquí?", False)

    elif nombre == "Lisa":
        acotacion("Lee la carta inconclusa en el suelo sin tocarla. "
                  "Se arrodilla para verla mejor y sus ojos recorren "
                  "las líneas dos veces, tres veces.")
        acotacion("Cuando se levanta, su expresión ha cambiado completamente: "
                  "ya no es la periodista calculadora que llegó al lobby.")
        dialogo("LISA", "No está muerto.")
        acotacion("Lo dice en voz muy baja.")
        dialogo("LISA", "Dios mío. No está muerto.", False)

    elif nombre == "Robert":
        acotacion("Lo dice mirando la habitación desde el umbral, sin entrar.")
        dialogo("ROBERT", "No debería estar aquí. Esta es la habitación de "
                "un hombre. Un espacio privado.")
        acotacion("Una pausa larga. Sus nudillos están blancos en el marco.")
        dialogo("ROBERT", "Simón y yo... nuestra relación era complicada. "
                "Más de lo que nadie sabe. Ojalá hubiera sido diferente. "
                "Eso es todo lo que puedo decir.", False)

    elif nombre == "Ana":
        dialogo("ANA", "El cajón de la mesita está entreabierto. La fotografía "
                "del niño. ¿La viste?")
        acotacion("Hay algo en su voz que es distinto a antes, más suave.")
        dialogo("ANA", "Simón nunca habló de su vida antes de ser Simón el "
                "pintor. Nunca. Como si hubiera decidido empezar a existir "
                "a los treinta y cinco años y punto.")
        dialogo("ANA", "Supongo que todos tenemos esa versión de nosotros "
                "que enterramos.", False)

    elif nombre == "Lucas":
        acotacion("Está mirando la fotografía del niño del cajón. No la toca.")
        dialogo("LUCAS", "Lucas. El nombre está escrito al dorso.")
        acotacion("Su voz es plana.")
        dialogo("LUCAS", "Hay un relicario que perteneció a Simón. Yo lo "
                "tengo, o lo tuve. Lo tomé sin permiso. Iba a devolverlo, "
                "siempre iba a devolverlo.")
        acotacion("Hace una pausa.")
        dialogo("LUCAS", "Si está aquí en algún lugar... si aparece entre "
                "sus cosas... necesito que no se asocie conmigo. ¿Entiendes "
                "lo que te estoy diciendo?", False)
    pausa()

# ══════════════════════════════════════════════════════════════
#  CAPÍTULO 4 — LA HORA DEL TALLER (7:00 PM)
# ══════════════════════════════════════════════════════════════

def capitulo_4():
    G.capitulo = 4
    titulo("C A P Í T U L O   4", "La Hora del Taller — 7:00 PM")
    time.sleep(0.5)

    narrar("Afuera ya casi no había luz. El ala sur de la mansión, donde "
           "estaba el taller, tenía los tragaluces del techo que ahora solo "
           "dejaban entrar la última luz cenicienta del día.")
    narrar("Alguien —ninguno de los cinco quiso decir quién— había encendido "
           "las luces interiores de la galería: unas tiras de luz fría que "
           "iluminaban los cuadros desde abajo, como en una exposición real.")
    pausa()

    explorar_galeria()
    interacciones_c4()

    titulo("D E C I S I Ó N", "Capítulo 4")
    if G.codigo_encontrado:
        narrar("Tienes el código: 4-7-2-9. El mapa de la habitación marcaba "
               "algo en el sótano. Lucas mencionó que cuatro dígitos podrían "
               "ser un código de acceso.")
    narrar("La noche se acerca. La mansión cambia cuando oscurece.")
    e = elegir([
        "Bajar al sótano a buscar la sala de seguridad" if G.codigo_encontrado
            else "Volver a la habitación de Simón a buscar más pistas",
        "Confrontar al grupo: exigir que todos digan la verdad",
        "Mantener al grupo unido y compartir todo lo descubierto",
    ])
    if e == 1:
        if G.codigo_encontrado:
            G.decidir("sotano_c4")
            narrar("El grupo baja al sótano. La puerta tiene un teclado "
                   "numérico. Introduces 4-7-2-9. Un clic. La puerta se abre.")
            G.guardar_pista("sala_camaras_abierta")
        else:
            G.decidir("volver_habitacion_c4")
            narrar("Vuelves a la habitación. Esta vez notas algo que antes "
                   "pasaste por alto: el mapa tiene una marca en el sótano.")
            G.guardar_pista("mapa_ala_norte")
    elif e == 2:
        G.decidir("confrontar_grupo_c4")
        narrar("El silencio que sigue a tu exigencia es el más largo de "
               "toda la tarde. Uno a uno, las máscaras empiezan a caer.")
        dialogo("BEN", "Hice cosas que no debería haber hecho. Cosas que "
                "tienen que ver con dinero y con la confianza que Simón me dio.")
        dialogo("ANA", "Las joyas. Necesito recuperar las joyas antes de "
                "que alguien descubra que estuvieron en mi poder.")
        acotacion("Robert no dice nada. Lucas mira al suelo. Lisa toma notas.")
        for n in G.presentes():
            G.p(n).aislar(10)
            G.p(n).conectar(5)
        G.guardar_pista("verdades_parciales")
    else:
        G.decidir("compartir_c4")
        narrar("El grupo se reúne en el centro de la galería, bajo el cuadro "
               "de los cinco visitantes. Por primera vez desde que llegaron, "
               "hablan de verdad. No de Simón. De ellos mismos.")
        narrar("No es una confesión completa. Pero es un comienzo. "
               "Y a veces un comienzo es suficiente para que la soledad "
               "retroceda un paso.")
        for n in G.presentes(): G.p(n).conectar(15)
        G.guardar_pista("grupo_comparte")

    _cierre_capitulo()


def explorar_galeria():
    titulo("L A   G A L E R Í A", "Exploración libre")
    narrar("Cuadros en distintos estados de terminación cubren las paredes. "
           "Hay manchas de pintura en el suelo, frascos de pigmento, trapos "
           "sucios. En el centro, una tela grande cubierta con una sábana "
           "blanca. El espacio huele a trementina y a algo metálico.")
    visto = set()
    while True:
        ops = []
        if "sabana" not in visto:
            ops.append("Levantar la sábana del cuadro central")
        if "grabador" not in visto:
            ops.append("Reproducir el grabador de audio en la repisa")
        if "codigo" not in visto:
            ops.append("Examinar el cuadro abstracto con números en la firma")
        if "mancha" not in visto:
            ops.append("Investigar la mancha oscura cerca de la puerta trasera")
        if "lienzos" not in visto:
            ops.append("Buscar entre los lienzos apoyados en la pared")
        ops.append("Terminar de explorar")
        e = elegir(ops)
        sel = ops[e - 1]

        if "sábana" in sel:
            visto.add("sabana")
            narrar("Al levantar la sábana se revela un cuadro inacabado. "
                   "Representa a cinco personas de pie en un espacio que "
                   "claramente es el lobby de la mansión. Sus rostros están "
                   "apenas esbozados, pero sus posturas son identificables.")
            narrar("En el margen inferior, escrito con pintura fresca:")
            dialogo("CUADRO", "Los que llegaron a buscar.")
            acotacion("Simón los pintó. Antes de que llegaran. "
                      "Sabía que vendrían. Sabía quiénes serían.")
            G.guardar_pista("cuadro_cinco")

        elif "grabador" in sel:
            visto.add("grabador")
            narrar("Un pequeño grabador digital sobre la repisa, con la "
                   "pantalla encendida en pausa. Al reproducirlo se escucha "
                   "la voz de Simón, inconfundible:")
            dialogo("SIMÓN", "Están en la casa. No sé cuántos. Pero no son "
                    "todos enemigos. Algunos solo tienen miedo.")
            acotacion("La voz es reciente. Cansada pero firme. "
                      "La voz de alguien que todavía tiene algo por lo que luchar.")
            G.guardar_pista("grabacion_simon")

        elif "números" in sel:
            visto.add("codigo")
            narrar("Uno de los cuadros terminados, una composición abstracta, "
                   "tiene una serie de números escritos en el ángulo inferior "
                   "derecho que parecen parte de la firma.")
            narrar("Los números son: 4 - 7 - 2 - 9")
            acotacion("No son números de catálogo. Son demasiado cortos. "
                      "Cuatro dígitos. Un código.")
            G.guardar_pista("codigo_4729")
            G.codigo_encontrado = True

        elif "mancha" in sel:
            visto.add("mancha")
            narrar("Cerca de la puerta trasera del taller hay una mancha "
                   "oscura en el suelo de madera. Pequeña, reciente, "
                   "semicubierta por un trapo como si alguien intentó "
                   "limpiarla con prisa.")
            acotacion("No es pintura. Es sangre. Alguien fue herido aquí. "
                      "O llevado desde aquí.")
            G.guardar_pista("mancha_sangre")

        elif "lienzos" in sel:
            visto.add("lienzos")
            narrar("Oculta entre varios lienzos apoyados en la pared hay "
                   "una carpeta de plástico transparente con fotografías "
                   "y documentos. Las fotos muestran el exterior de un "
                   "almacén en llamas. Los documentos son copias de "
                   "declaraciones juradas.")
            acotacion("La evidencia que Lisa vino a buscar. Está aquí, "
                      "escondida entre el arte de Simón.")
            G.guardar_pista("carpeta_lisa")
        else:
            break


def interacciones_c4():
    titulo("L A   G A L E R Í A", "Interacciones — Capítulo 4")
    hablados = set()
    while True:
        vivos = [n for n in G.presentes() if n not in hablados]
        if not vivos: break
        ops = [f"Hablar con {n}" for n in vivos] + ["No hablar con nadie más"]
        e = elegir(ops)
        if e > len(vivos): break
        nombre = vivos[e - 1]
        hablados.add(nombre)
        G.p(nombre).conectar(20)
        _dialogo_c4(nombre)


def _dialogo_c4(nombre):
    separador()
    if nombre == "Robert":
        acotacion("Está frente al cuadro descubierto, estudiando las figuras. "
                  "Se reconoce a sí mismo en la del fondo, la más retirada.")
        dialogo("ROBERT", "Nos conocía bien. Demasiado bien.")
        acotacion("Se gira hacia ti.")
        dialogo("ROBERT", "Hay una carta. En algún lugar de esta casa hay "
                "una carta que no debería existir o que, si existe, debería "
                "haber llegado a mí hace años. Si la encuentras...", False)
        acotacion("No termina la petición. Pero el significado es claro.")

    elif nombre == "Ana":
        dialogo("ANA", "Ese cuadro lo empezó hace dos meses. Lo reconozco "
                "por la preparación de la tela, es su técnica de los últimos "
                "años. Dos meses atrás, Simón estaba vivo y pintando.")
        acotacion("Te mira directamente.")
        dialogo("ANA", "Alguien mintió sobre su muerte. La pregunta es si "
                "ese alguien está en esta habitación con nosotros ahora mismo.", False)

    elif nombre == "Ben":
        acotacion("Ben ha encontrado el grabador antes que tú. Cuando llegas, "
                  "está escuchando con el grabador pegado al oído, los ojos "
                  "cerrados. Al darse cuenta de que no está solo, lo baja.")
        dialogo("BEN", "Era su voz. La grabación. Era él.")
        acotacion("Traga saliva.")
        dialogo("BEN", "Mira, yo hice cosas que no debería haber hecho. "
                "Cosas que tienen que ver con dinero y con la confianza que "
                "Simón me dio. Y si está vivo... hay cosas que tendría que "
                "explicarle. Cosas que no sé cómo explicar.", False)

    elif nombre == "Lisa":
        dialogo("LISA", "La mancha del suelo, cerca de la puerta trasera. "
                "Eso no es pintura. Conozco la diferencia.")
        acotacion("Saca su teléfono y hace una foto desde lejos.")
        dialogo("LISA", "Simón fue atacado aquí. O llevado desde aquí. "
                "Lo que significa que quien lo tiene está en la casa y "
                "probablemente sabe que estamos buscando. Necesitamos "
                "encontrarlo antes de que oscurezca del todo.", False)

    elif nombre == "Lucas":
        acotacion("Lucas está mirando un cuadro: un retrato de un niño "
                  "pequeño que mira hacia arriba. El niño tiene el mismo "
                  "relicario de plata en el cuello.")
        dialogo("LUCAS", "Hay un cuadro con una serie de números en la firma. "
                "Lo vi hace un momento. No son números de catálogo. Son "
                "demasiado cortos. Cuatro dígitos.")
        dialogo("LUCAS", "¿Para qué necesitaría Simón un código de cuatro "
                "dígitos en un espacio como este?", False)
    pausa()

# ══════════════════════════════════════════════════════════════
#  CAPÍTULO 5 — LA NOCHE (10:00 PM)
# ══════════════════════════════════════════════════════════════

def capitulo_5():
    G.capitulo = 5
    titulo("C A P Í T U L O   5", "La Noche — 10:00 PM")
    time.sleep(0.5)

    narrar("La mansión a las diez de la noche era un organismo distinto. "
           "Los ruidos de la madera al asentarse, el viento que encontraba "
           "grietas en las ventanas mal selladas del pasillo norte, el "
           "zumbido sordo de los equipos electrónicos en el sótano.")
    n_vivos = len(G.presentes())
    if n_vivos == 5:
        narrar("El grupo había permanecido unido más tiempo del que "
               "cualquiera habría predicho. Nadie lo decía, pero todos "
               "lo sentían: en conjunto eran más seguros que solos.")
    elif n_vivos >= 3:
        narrar("El grupo se había reducido. Los que quedaban se miraban "
               "con una mezcla de desconfianza y necesidad. Cada ausencia "
               "pesaba como una acusación silenciosa.")
    else:
        narrar("Quedaban pocos. La mansión se sentía más grande con cada "
               "persona que se iba. Los pasillos eran más largos, las "
               "sombras más densas, el silencio más absoluto.")
    pausa()

    # ── Sala de cámaras ──
    if G.codigo_encontrado or G.tiene("sala_camaras_abierta"):
        explorar_sala_camaras()
    else:
        titulo("E L   S Ó T A N O")
        narrar("Bajas al sótano. Hay una puerta con un teclado numérico. "
               "Sin el código, no puedes entrar.")
        e = elegir([
            "Intentar combinaciones al azar",
            "Volver arriba y buscar el código",
            "Forzar la puerta",
        ])
        if e == 1:
            narrar("Pruebas varias combinaciones. Ninguna funciona. "
                   "Pero al tercer intento, recuerdas algo: el cuadro "
                   "abstracto en la galería tenía números en la firma.")
            e2 = elegir(["Ir a la galería a buscar el código", "Rendirse"])
            if e2 == 1:
                narrar("Vuelves a la galería. Los números: 4-7-2-9. "
                       "Corres al sótano. El código funciona.")
                G.codigo_encontrado = True
                G.guardar_pista("codigo_4729")
                explorar_sala_camaras()
            else:
                narrar("Sin la sala de cámaras, tendrás que buscar a Simón "
                       "a ciegas en el ala norte.")
        elif e == 2:
            narrar("Subes a la galería. El cuadro abstracto tiene los números "
                   "4-7-2-9 en la firma. Vuelves al sótano. Funciona.")
            G.codigo_encontrado = True
            G.guardar_pista("codigo_4729")
            explorar_sala_camaras()
        else:
            narrar("La puerta no cede. Está diseñada para resistir. "
                   "Tendrás que buscar a Simón sin la información "
                   "de las cámaras.")

    # ── Los objetos ──
    titulo("L O S   O B J E T O S", "Cada uno encuentra lo que vino a buscar")
    narrar("Antes de ir al ala norte, cada uno tiene una última oportunidad "
           "de encontrar lo que vino a buscar. Ayudarlos fortalece el vínculo. "
           "Ignorarlos los empuja más cerca del borde.")
    for nombre in list(G.presentes()):
        p = G.p(nombre)
        if p.objeto_encontrado:
            continue
        separador()
        print(f"  {nombre.upper()} busca: {p.objeto}")
        print(f"  Ubicación: {p.ubicacion_obj}")
        e = elegir([
            f"Ayudar a {nombre} a encontrar su objeto",
            "Dejarlo por su cuenta",
        ])
        if e == 1:
            p.conectar(20)
            p.objeto_encontrado = True
            _encontrar_objeto(nombre)
        else:
            p.aislar(15)
            acotacion(f"{nombre} te mira un momento. Asiente despacio. "
                      f"Se aleja solo hacia {p.ubicacion_obj.lower()}.")

    # ── El rescate ──
    el_rescate()

    G.fin_capitulo()
    abandonado = G.verificar_abandonos()
    if abandonado:
        _escena_abandono(abandonado)


def explorar_sala_camaras():
    titulo("S A L A   D E   C Á M A R A S", "Sótano de la mansión")
    narrar("Una habitación pequeña y sin ventanas. Una hilera de monitores "
           "mostraba las cámaras de cada habitación de la casa, aunque "
           "varios están apagados o con la señal cortada.")
    narrar("Hay una silla giratoria frente a los monitores, y en ella, "
           "abandonado, un maletín de cuero negro. Los monitores que aún "
           "funcionan muestran pasillos vacíos y una habitación con una "
           "figura sentada, aunque la imagen es demasiado granulada.")
    visto = set()
    while True:
        ops = []
        if "monitor" not in visto:
            ops.append("Examinar el monitor central activo")
        if "maletin" not in visto:
            ops.append("Abrir el maletín de cuero negro")
        if "disco" not in visto:
            ops.append("Revisar el disco duro externo")
        if "nota_roja" not in visto:
            ops.append("Leer la nota con marcador rojo en el monitor")
        if "mapa_nuevo" not in visto:
            ops.append("Estudiar el mapa actualizado")
        ops.append("Continuar")
        e = elegir(ops)
        sel = ops[e - 1]

        if "monitor central" in sel:
            visto.add("monitor")
            narrar("La imagen muestra una figura humana sentada en una silla "
                   "en una habitación que podría ser cualquiera de las cinco "
                   "del ala norte. La figura no se mueve. No es posible "
                   "determinar si está atada o simplemente inmóvil.")
            G.guardar_pista("figura_monitor")

        elif "maletín" in sel:
            visto.add("maletin")
            narrar("Dentro del maletín negro hay, entre otros objetos, un "
                   "relicario de plata antiguo. En su interior, grabado:")
            dialogo("RELICARIO", "Para Lucas. Siempre.")
            G.guardar_pista("relicario_encontrado")
            G.p("Lucas").objeto_encontrado = True
            if "Lucas" in G.presentes():
                G.p("Lucas").conectar(20)

        elif "disco duro" in sel:
            visto.add("disco")
            narrar("Los archivos tienen fechas de los últimos seis meses. "
                   "El archivo más reciente, de hace dos días, muestra a "
                   "Simón hablando con alguien fuera de cuadro. Simón dice:")
            dialogo("SIMÓN", "No voy a callar más. Aunque eso me cueste la vida.")
            G.guardar_pista("grabacion_amenaza")

        elif "nota" in sel:
            visto.add("nota_roja")
            narrar("Escrita con marcador rojo sobre un papel:")
            dialogo("NOTA", "Si encuentras esto, ya saben que estás aquí. "
                    "No uses las luces del pasillo norte.")
            G.guardar_pista("advertencia_norte")

        elif "mapa" in sel:
            visto.add("mapa_nuevo")
            narrar("Una versión más reciente del mapa dibujado a mano. "
                   "Una habitación del ala norte está marcada con una X roja "
                   "y la palabra 'aquí' escrita al lado. Es la misma "
                   "habitación que aparece en el monitor.")
            G.guardar_pista("ubicacion_simon")
        else:
            break


def _encontrar_objeto(nombre):
    if nombre == "Ben":
        narrar("Ben encuentra el sobre con efectivo y el libro de cuentas "
               "en la habitación de Simón, donde Simón lo había dejado "
               "para que Ben lo encontrara.")
        narrar("Dentro del sobre hay una nota de puño y letra del pintor:")
        dialogo("SIMÓN (nota)", "Ya lo sé. Siempre lo supe. Pero confié "
                "en que lo arreglarías.")
        acotacion("Ben tardó un momento en poder moverse después de leerla. "
                  "Sus ojos se llenaron de algo que no era miedo. Era vergüenza.")

    elif nombre == "Lisa":
        narrar("Lisa encuentra la carpeta entre los lienzos de la galería. "
               "Las fotografías, los documentos, las declaraciones juradas: "
               "todo está ahí. La evidencia que necesitaba para terminar "
               "lo que había empezado.")
        acotacion("La guarda sin decir nada. Pero sus manos tiemblan.")

    elif nombre == "Robert":
        narrar("Robert encuentra el sobre con su nombre en el cajón de la "
               "cómoda del lobby. Lo abre con manos que no tiemblan porque "
               "había decidido no dejarlas temblar.")
        narrar("Lee la carta del padre dos veces. La dobla y se la mete "
               "en el bolsillo interior del saco.")
        acotacion("No dice nada. Pero algo en su postura cambia, como si "
                  "un peso que llevaba décadas cargando se hubiera movido "
                  "de un hombro al otro.")

    elif nombre == "Ana":
        if G.tiene("llave_pequena"):
            narrar("Ana usa la llave pequeña del cajón de la mesita de Simón. "
                   "Encaja perfectamente en el archivador del estudio. "
                   "El estuche de cuero está adentro. Las joyas están intactas.")
        else:
            narrar("Ana encuentra el estuche de cuero en el cajón cerrado "
                   "del estudio. Alguien lo había dejado entreabierto.")
        acotacion("Las guarda sin decir nada. Pero sus ojos se cierran "
                  "un momento, como quien exhala después de contener "
                  "la respiración demasiado tiempo.")

    elif nombre == "Lucas":
        if G.tiene("relicario_encontrado"):
            narrar("Lucas ya tiene el relicario. Lo sostiene en la palma "
                   "de la mano, leyendo la inscripción una vez más.")
        else:
            narrar("Lucas encuentra el relicario en el maletín de la sala "
                   "de cámaras. Lo toma con ambas manos, lo abre y lee "
                   "la inscripción interior: 'Para Lucas. Siempre.'")
        acotacion("Lo cierra. Lo guarda. Toma una decisión silenciosa "
                  "que nadie más ve.")
    pausa()

# ══════════════════════════════════════════════════════════════
#  EL RESCATE
# ══════════════════════════════════════════════════════════════

def el_rescate():
    titulo("E L   R E S C A T E", "Ala Norte — Pasillo oscuro")
    narrar("El pasillo norte era exactamente como la nota advertía: largo, "
           "oscuro, con el tipo de silencio que no es ausencia de sonido "
           "sino presencia de algo que aguarda.")
    if G.tiene("advertencia_norte"):
        narrar("No usan las luces. Usan las linternas de los teléfonos, "
               "apuntando al suelo.")
    else:
        narrar("Encienden las luces del pasillo. El fluorescente parpadea "
               "dos veces antes de estabilizarse. Desde algún lugar de la "
               "casa, un sonido. Como una puerta que se cierra.")
        for n in G.presentes(): G.p(n).aislar(5)

    narrar("Hay cinco puertas. Todas cerradas. Todas iguales.")
    pausa()

    if G.tiene("ubicacion_simon"):
        narrar("El mapa actualizado señala la tercera puerta con una X roja "
               "y la palabra 'aquí'. Pero en la oscuridad, frente a cinco "
               "puertas idénticas, la certeza se vuelve más frágil.")
    e = elegir([
        "Abrir la primera puerta (más cercana a la escalera)",
        "Abrir la tercera puerta (la que señala el mapa)" if G.tiene("ubicacion_simon")
            else "Abrir la tercera puerta (intuición)",
        "Abrir la quinta puerta (al fondo del pasillo)",
    ])

    if e == 2:
        G.simon_encontrado = True
        _escena_rescate_directo()
    elif e == 1:
        narrar("La primera habitación está vacía. Una silla, una mesa, "
               "nada más. Pero en la mesa hay una nota:")
        dialogo("NOTA", "Más adelante.")
        narrar("Abres la siguiente puerta. Y la siguiente.")
        G.simon_encontrado = True
        _escena_rescate_directo()
        acotacion("Perdiste tiempo. Pero lo encontraste.")
        for n in G.presentes(): G.p(n).aislar(5)
    else:
        narrar("Al fondo del pasillo, la quinta puerta. La abres.")
        narrar("No es Simón. Es una habitación vacía con un espejo "
               "en la pared opuesta. Tu propio reflejo te devuelve "
               "la mirada en la oscuridad.")
        narrar("Un sonido detrás de ti. Pasos. Alguien más está en "
               "el pasillo. Alguien que no es del grupo.")
        acotacion("Retrocedes. El grupo se reagrupa. Abren la tercera puerta.")
        G.simon_encontrado = True
        _escena_rescate_directo()
        for n in G.presentes(): G.p(n).aislar(10)


def _escena_rescate_directo():
    separador()
    narrar("La puerta se abre.")
    time.sleep(0.5)
    narrar("Simón está sentado en una silla, con las manos atadas con una "
           "cuerda fina al respaldo, una venda en la frente y una expresión "
           "que tarda un segundo en transformarse de blankness absoluta "
           "a reconocimiento.")
    time.sleep(0.5)
    dialogo("SIMÓN", "Sabía que vendría alguien.")
    acotacion("Su voz es ronca de llevar horas sin agua, pero firme.")
    dialogo("SIMÓN", "No sabía quiénes.")
    time.sleep(0.5)

    n_vivos = len(G.presentes())
    if n_vivos == 5:
        narrar("Cuando vio los cinco rostros iluminados por las linternas, "
               "algo en él se relajó de una forma que era casi visible, "
               "como si un músculo que llevaba días tenso decidiera "
               "por fin soltarse.")
        dialogo("SIMÓN", "Todos. Vinieron todos.")
    elif n_vivos >= 3:
        narrar("Simón contó los rostros. Su expresión cambió levemente "
               "al notar las ausencias.")
        dialogo("SIMÓN", "No están todos.")
        acotacion("No es una pregunta. Es una constatación.")
    else:
        narrar("Simón miró los pocos rostros frente a él. "
               "Algo en sus ojos se apagó un momento.")
        dialogo("SIMÓN", "¿Solo ustedes?")
    pausa()

    # ── Escena del rescate según quién está ──
    vivos = G.presentes()
    if "Ben" in vivos:
        narrar("Ben fue el primero en arrodillarse para desatar las cuerdas. "
               "Sus manos no temblaban, aunque quizás debían hacerlo.")
    if "Robert" in vivos:
        narrar("Robert se mantuvo de pie en el umbral, rígido, pero no se fue.")
    if "Ana" in vivos:
        narrar("Ana sostuvo la linterna para que pudieran ver mejor el nudo.")
    if "Lisa" in vivos:
        narrar("Lisa grabó el estado de la habitación con su teléfono, "
               "metódica incluso en ese momento.")
    if "Lucas" in vivos:
        narrar("Lucas fue el último en entrar al cuarto, y cuando lo hizo, "
               "sacó el relicario del bolsillo y lo colocó con cuidado "
               "sobre la pequeña mesa junto a la silla de Simón, sin decir nada.")
        time.sleep(0.5)
        dialogo("SIMÓN", "Ya sé lo que tomaste. Y ya sé por qué.")
        time.sleep(0.3)
        dialogo("SIMÓN", "Está bien.")
    pausa()

    # ── Decisión final ──
    titulo("L A   Ú L T I M A   D E C I S I Ó N")
    narrar("Simón está libre. Las cuerdas están en el suelo. "
           "El grupo —lo que queda de él— está reunido en el pasillo norte.")
    narrar("Nadie preguntó qué había pasado exactamente. No esa noche. "
           "Había tiempo para las preguntas, para las explicaciones, "
           "para los secretos que cada uno tendría que decidir si revelaba "
           "o guardaba.")
    escribir_lento("Esa noche solo había que salir de la mansión.")
    pausa()

    narrar("Pero antes de salir, una última decisión.")
    e = elegir([
        "Salir todos juntos ahora mismo, sin mirar atrás",
        "Quedarse un momento más — dejar que cada uno se despida del lugar",
        "Buscar al asesino antes de irse",
    ])
    G.decidir(f"final_c5_{e}")

    if e == 1:
        G.decidir("salir_juntos")
        narrar("El grupo camina hacia la puerta principal. Nadie habla. "
               "Los pasos de todos suenan al unísono sobre la madera vieja.")
        for n in G.presentes(): G.p(n).conectar(10)
    elif e == 2:
        G.decidir("despedida")
        narrar("Cada uno se toma un momento. Ben mira el estudio una última "
               "vez. Robert toca el marco de la puerta del lobby como "
               "despidiéndose de algo que nunca tuvo. Ana recorre la galería "
               "con los ojos. Lisa guarda su grabadora sin usarla. "
               "Lucas mira la fachada desde la ventana.")
        for n in G.presentes(): G.p(n).conectar(15)
    else:
        G.decidir("buscar_asesino")
        narrar("Recorren la mansión. Cada habitación, cada pasillo, cada "
               "rincón. No encuentran a nadie. El asesino se fue, o se "
               "escondió en un lugar que la mansión no quiso revelar.")
        narrar("Algunas preguntas, la mansión se las quedó.")
        for n in G.presentes(): G.p(n).aislar(5)

# ══════════════════════════════════════════════════════════════
#  FINALES
# ══════════════════════════════════════════════════════════════

def determinar_final():
    vivos = G.presentes()
    n = len(vivos)
    objetos = sum(1 for p in G.personajes.values() if p.objeto_encontrado)

    if G.simon_encontrado and n == 5 and objetos == 5:
        final_perfecto(vivos)
    elif G.simon_encontrado and n >= 4:
        final_bueno(vivos, n, objetos)
    elif G.simon_encontrado and n >= 2:
        final_agridulce(vivos, n, objetos)
    elif G.simon_encontrado and n >= 1:
        final_solitario(vivos, objetos)
    else:
        final_oscuro()


def final_perfecto(vivos):
    titulo("✦   L A   M A N S I Ó N   L O S   S O L T Ó   ✦",
           "Todos vivos · Todos los objetos · Simón rescatado")
    time.sleep(1)
    narrar("Salieron juntos. Los seis.")
    time.sleep(0.5)
    narrar("El asesino no los siguió. O no pudo. O decidió no hacerlo. "
           "Nadie lo vio salir, ni esa noche ni ninguna otra. Nadie supo "
           "nunca quién era con certeza, ni qué había querido realmente.")
    escribir_lento("Algunas preguntas, la mansión se las quedó.")
    pausa()

    narrar("Afuera, el aire de la noche estaba frío y limpio.")
    narrar("Ben miró el cielo. Robert abrió la puerta de su coche y se "
           "quedó parado junto a ella un momento antes de subir. Ana llamó "
           "a alguien desde su teléfono en voz muy baja. Lisa sacó su "
           "grabadora de periodista y la guardó sin usarla. Lucas miró "
           "la fachada de la mansión una última vez.")
    pausa()

    narrar("Simón se sentó en el escalón de la entrada, con las muñecas "
           "todavía enrojecidas por las cuerdas, y respiró el aire exterior "
           "como si fuera la primera vez.")
    time.sleep(1)
    escribir_lento("Nadie le preguntó qué iba a pasar ahora.")
    escribir_lento("Nadie necesitó hacerlo.")
    time.sleep(1)
    print(f"\n{'✦  F I N  ✦':^{W}}\n")
    print(f"\033[2m{'La Mansión de Simón':^{W}}\033[0m\n")


def final_bueno(vivos, n, objetos):
    titulo("◆   V E R D A D   A   M E D I A S   ◆",
           f"{n} sobrevivientes · Simón rescatado")
    time.sleep(1)
    narrar(f"Salieron {n + 1} personas de la mansión esa noche. "
           f"No todos los que entraron.")
    ausentes = [n for n, p in G.personajes.items() if not p.presente]
    if ausentes:
        narrar(f"{''.join(ausentes)} no estaba{'n' if len(ausentes) > 1 else ''} "
               f"cuando abrieron la puerta principal. "
               f"El aislamiento los había empujado fuera antes de que "
               f"la historia terminara.")
    pausa()
    narrar("Simón fue rescatado. Eso era lo que importaba. Los que se "
           "fueron antes de llegar al final cargaron con sus secretos "
           "hacia algún lugar que nadie conoce.")
    narrar("La mansión quedó en silencio detrás de ellos. Algunas puertas "
           "quedaron cerradas. Algunos secretos quedaron sin dueño.")
    escribir_lento("Pero los que salieron, salieron juntos.")
    time.sleep(1)
    print(f"\n{'◆  F I N  ◆':^{W}}\n")
    print(f"\033[2m{'La Mansión de Simón':^{W}}\033[0m\n")


def final_agridulce(vivos, n, objetos):
    titulo("▲   E L   C O S T O   D E L   S I L E N C I O   ▲",
           f"{n} sobrevivientes · Simón rescatado")
    time.sleep(1)
    narrar("El aislamiento hizo su trabajo. Uno a uno, los que no "
           "encontraron razón para quedarse se fueron. La mansión los "
           "absorbió en silencio, como absorbe el polvo y los secretos.")
    pausa()
    narrar("Simón fue rescatado, pero el grupo que lo encontró era una "
           "sombra de lo que llegó esa tarde. Los secretos que nadie "
           "compartió resultaron más peligrosos que el asesino.")
    narrar(f"Solo {', '.join(vivos)} estaban ahí cuando Simón respiró "
           f"el aire de la noche. Los demás ya eran recuerdos.")
    escribir_lento("A veces sobrevivir no es suficiente.")
    time.sleep(1)
    print(f"\n{'▲  F I N  ▲':^{W}}\n")
    print(f"\033[2m{'La Mansión de Simón':^{W}}\033[0m\n")


def final_solitario(vivos, objetos):
    titulo("●   S O L O   ●", "Un sobreviviente · Simón rescatado")
    time.sleep(1)
    nombre = vivos[0]
    narrar(f"Al final, solo quedaban {nombre} y Simón. Dos personas en una "
           f"mansión construida para contener los secretos de muchos.")
    narrar("Los demás se fueron. Uno a uno, el aislamiento los empujó "
           "hacia la puerta, hacia la noche, hacia el silencio de sus "
           "propias verdades sin resolver.")
    pausa()
    narrar(f"{nombre} desató a Simón en silencio. No hubo palabras de "
           f"alivio ni abrazos de reencuentro. Solo dos personas cansadas "
           f"caminando por un pasillo oscuro hacia una puerta que daba "
           f"al exterior.")
    narrar("Afuera, el aire estaba frío. La mansión se quedó atrás, "
           "con sus puertas cerradas y sus preguntas sin respuesta.")
    escribir_lento("Algunas historias no tienen final feliz.")
    escribir_lento("Solo tienen final.")
    time.sleep(1)
    print(f"\n{'●  F I N  ●':^{W}}\n")
    print(f"\033[2m{'La Mansión de Simón':^{W}}\033[0m\n")


def final_oscuro():
    titulo("■   L O   Q U E   L A   M A N S I Ó N   S E   Q U E D Ó   ■",
           "Simón no fue encontrado")
    time.sleep(1)
    narrar("La soledad fue el arma más eficaz. No el asesino, no la "
           "oscuridad, no los secretos. La soledad.")
    narrar("Uno a uno, el grupo se deshizo. Cada uno se fue con su razón "
           "y sin encontrar lo que buscaba. Simón sigue en algún lugar "
           "del ala norte. La mansión no reveló su secreto.")
    pausa()
    narrar("Los cinco visitantes volvieron a sus vidas como si esa tarde "
           "no hubiera existido. Pero todos, sin excepción, sueñan a veces "
           "con un pasillo largo y oscuro, con cinco puertas cerradas, "
           "y con una voz ronca que dice:")
    dialogo("SIMÓN", "Sabía que vendría alguien.")
    time.sleep(0.5)
    escribir_lento("Nadie vino.")
    time.sleep(1)
    narrar("Algunas noches, desde la carretera, se puede ver una luz "
           "en una de las ventanas del ala norte.")
    escribir_lento("Nadie sabe quién la enciende.")
    time.sleep(1)
    print(f"\n{'■  F I N  ■':^{W}}\n")
    print(f"\033[2m{'La Mansión de Simón':^{W}}\033[0m\n")

# ══════════════════════════════════════════════════════════════
#  UTILIDADES DE CIERRE Y RESUMEN
# ══════════════════════════════════════════════════════════════

def _cierre_capitulo():
    G.fin_capitulo()
    abandonado = G.verificar_abandonos()
    if abandonado:
        _escena_abandono(abandonado)
    G.mostrar_grupo()
    pausa()


def _escena_abandono(nombre):
    titulo(f"⚠   {nombre.upper()} SE VA   ⚠")
    time.sleep(0.5)
    textos = {
        "Ben": ("Ben se levantó sin decir nada. Tomó su saco del respaldo "
                "de la silla, se lo puso con movimientos mecánicos y caminó "
                "hacia la puerta principal. Nadie lo detuvo. En el umbral "
                "se detuvo un momento, como si esperara que alguien dijera "
                "algo. Nadie dijo nada. La puerta se cerró detrás de él "
                "con un sonido que era demasiado suave para lo que significaba."),
        "Lisa": ("Lisa guardó su grabadora en el bolso con la calma de "
                 "alguien que ya tomó una decisión. 'No vine aquí para esto,' "
                 "dijo sin mirar a nadie. 'Vine por la evidencia. Si nadie "
                 "va a ayudarme a encontrarla, la buscaré por mi cuenta.' "
                 "Salió por la puerta trasera. El jardín se la tragó."),
        "Robert": ("Robert se puso de pie con la dignidad rígida de un hombre "
                   "que ha pasado toda su vida controlando cómo lo ven los demás. "
                   "'Esto no es lo que me dijeron que sería,' murmuró. "
                   "Bajó las escaleras con pasos medidos. La puerta principal "
                   "se abrió y se cerró. El motor de su coche arrancó afuera."),
        "Ana": ("Ana recogió su bolso del sillón del lobby con movimientos "
                "precisos. 'Las joyas,' dijo en voz baja, más para sí misma "
                "que para nadie. 'Solo necesitaba las joyas.' Miró al grupo "
                "una última vez con una expresión que podría haber sido "
                "disculpa o podría haber sido alivio. Se fue sin despedirse."),
        "Lucas": ("Lucas se quitó los auriculares del cuello y los guardó "
                  "en la mochila. 'No puedo quedarme,' dijo con la voz plana "
                  "de alguien que ha tomado una decisión que le duele pero "
                  "que no va a cambiar. 'Lo siento.' Caminó hacia la puerta "
                  "con la mochila al hombro, como había llegado. "
                  "Como si las últimas horas no hubieran existido."),
    }
    narrar(textos.get(nombre, f"{nombre} se fue en silencio."))
    acotacion(f"El aislamiento de {nombre} superó el umbral crítico. "
              f"La soledad ganó esta vez.")
    pausa()


def resumen_final():
    titulo("R E S U M E N   D E   P A R T I D A")
    vivos = G.presentes()
    objetos = sum(1 for p in G.personajes.values() if p.objeto_encontrado)

    print(f"  Sobrevivientes     : {len(vivos)}/5")
    for n in vivos:
        obj = "✓" if G.p(n).objeto_encontrado else "✗"
        print(f"    {n:8s}  {obj} {G.p(n).objeto}")
    ausentes = [n for n, p in G.personajes.items() if not p.presente]
    if ausentes:
        print(f"\n  Abandonaron        : {', '.join(ausentes)}")
    print(f"\n  Simón rescatado    : {'Sí' if G.simon_encontrado else 'No'}")
    print(f"  Pistas descubiertas: {len(G.pistas)}")
    print(f"  Decisiones tomadas : {len(G.decisiones)}")

    separador()
    print("  Pistas clave:")
    claves = [
        ("simon_vivo",         "Carta inconclusa: 'No estoy muerto'"),
        ("grabacion_simon",    "Grabación de Simón: 'No son todos enemigos'"),
        ("codigo_4729",        "Código 4-7-2-9 del cuadro abstracto"),
        ("mancha_sangre",      "Mancha de sangre en la galería"),
        ("foto_cinta_negra",   "Sexta fotografía con rostro cubierto"),
        ("ubicacion_simon",    "Mapa con ubicación exacta de Simón"),
        ("grabacion_amenaza",  "Grabación: 'No voy a callar más'"),
        ("sobre_testigo",      "Sobre marcado TESTIGO"),
        ("segunda_copia",      "Simón tenía una segunda copia de seguridad"),
    ]
    encontradas = 0
    for k, desc in claves:
        if G.tiene(k):
            print(f"    ✓ {desc}")
            encontradas += 1
        else:
            print(f"    ✗ {desc}")
    print(f"\n  {encontradas}/{len(claves)} pistas clave encontradas")
    separador()


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    prologo()
    capitulo_1()
    capitulo_2()
    capitulo_3()
    capitulo_4()
    capitulo_5()
    determinar_final()
    resumen_final()
    print(f"\n{'Gracias por jugar La Mansión de Simón.':^{W}}")
    print(f"\033[2m{'Una historia de secretos, silencios y supervivencia':^{W}}\033[0m\n")

if __name__ == "__main__":
    main()
