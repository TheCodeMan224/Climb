# Desplegar Climb en Render

Climb es una app **Flet (Python)**. Render la corre como **servicio web** con
Python del lado servidor — así la API key y la base de datos quedan seguras.
(Netlify no sirve para esto porque solo hostea archivos estáticos, sin Python.)

## Requisitos previos
- El repo ya está en GitHub.
- Tu `ANTHROPIC_API_KEY` a la mano (NO se sube al repo; va en el panel de Render).

## Opción A — Blueprint (recomendada, usa `render.yaml`)
1. Entra a https://render.com → **New** → **Blueprint**.
2. Conecta tu repo de GitHub. Render leerá `render.yaml` y propondrá el servicio `climb`.
3. Antes de crear, ve a **Environment** y agrega la variable secreta:
   - `ANTHROPIC_API_KEY` = tu clave real.
4. **Apply** / **Create**. Render instala `requirements.txt` y corre `python main.py`.
5. Al terminar, te da una URL pública (p. ej. `https://climb-xxxx.onrender.com`).

## Opción B — Manual (sin Blueprint)
1. **New** → **Web Service** → conecta el repo.
2. Configura:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
3. En **Environment** agrega:
   - `ANTHROPIC_API_KEY` = tu clave
   - `PYTHON_VERSION` = `3.12.7`
4. **Create Web Service**.

## Cómo funciona el arranque
`main.py` detecta la variable `PORT` (que Render define):
- **Con PORT** → corre como servidor web (`view=WEB_BROWSER`, `host=0.0.0.0`).
- **Sin PORT** (tu máquina) → abre la app de escritorio, como siempre.

## Cosas que debes saber
- **Plan gratis:** el servicio se "duerme" tras ~15 min sin tráfico y despierta
  en la primera visita (tarda unos segundos la primera carga).
- **Base de datos:** en el plan gratis el disco es **efímero** → `climb.db` se
  reinicia en cada redeploy/reinicio. Para datos persistentes: un **Disco
  Persistente** (de pago) o migrar a **Render Postgres** (requiere cambios en la
  capa de datos).
- **Verificación de Flet web:** si el deploy arranca pero la web no carga, revisa
  los **logs** de Render. Puede que esta versión de Flet necesite componentes web
  extra; en ese caso, en `requirements.txt` usa `flet[all]==0.85.3` en vez de
  `flet==0.85.3`.

## Local sigue igual
`python main.py` en tu PC abre la app de escritorio, sin cambios.
