from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import traceback
import json
import ast
import os

# Leer archivos Parquet
df_gamesf1 = pd.read_parquet(r'DataApi/games_f1.parquet')
df_itemsf1 = pd.read_parquet(r'DataApi/items_new.parquet')
df_itemsf2 = pd.read_parquet(r'DataApi/items_reducido.parquet')
df_games_f3 = pd.read_csv(r'DataApi/df_games.csv')
df_reviews_f3 = pd.read_csv(r'DataApi/df_reviews.csv')
df_games_ML = pd.read_csv(r'DataApi/games_ML.csv')

app = FastAPI()

def PlayTimeGenre(genero: str):
    # Filtro el DataFrame df_games por el género especificado
    df_filtrado = df_gamesf1[df_gamesf1['genres'].str.contains(genero, case=False, na=False)]

    if not df_filtrado.empty:
        # Uno df_filtrado con df_items en item_id para obtener las horas jugadas
        df_merged = pd.merge(df_filtrado, df_itemsf1, left_on='id', right_on='item_id', how='inner')

        # Encontrar el año con más horas jugadas para el género
        año_max_horas = df_merged.groupby('release_date')['playtime_forever'].sum().idxmax()

        return {"Año de lanzamiento con más horas jugadas para género " + genero: año_max_horas}
    else:
        return {"mensaje": "No se encontraron juegos para el género especificado"}
@app.get("/playtime_genre/{genero}")
async def get_playtime_genre(genero: str):
    '''En esta funcion podras ingresar el genero de tu interes por ejemplo: Action,Casual,Indie,Simulation,
    Strategy. Y te devolvera el año de lanzamiento con mas horas jugadas
    '''    
    try:
        return PlayTimeGenre(genero)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    
df_users_recommend = pd.read_csv(r'DataApi/UsersRecommend.csv')
def UsersRecommend(año: int):
    try:
        # Filtra el DataFrame por el año especificado
        df_filtered = df_users_recommend[df_users_recommend['year'] == año]

        if not df_filtered.empty:
            # Ordena por el conteo de recomendaciones en orden descendente
            df_sorted = df_filtered.sort_values(by='count', ascending=False)

            # Obtiene el top 3 de juegos más recomendados
            top_3_recommended = df_sorted.head(3)['name'].tolist()

            # Crea la lista de retorno en el formato especificado
            return [{"Puesto " + str(i+1): juego} for i, juego in enumerate(top_3_recommended)]
        else:
            return {"mensaje": "No se encontraron juegos recomendados para el año especificado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Define ruta y método HTTP
@app.get("/users_recommend/{year}", response_model=list)
async def get_users_recommend(year: int):
    '''
    En esta funcion podras ingresar el año de tu interes y te devolvera un TOP 3 de los juegos 
    Mas recomendados para el año que ingresaste.
    '''
    try:
        return UsersRecommend(year)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/UsersNotRecommend')
def UsersNotRecommend(año: int):
    '''
    En esta funcion podras ingresar el año de tu interes, y te devolvera el TOP 3 de los juegos MENOS
    recomendados por los usuarios en ese año
    '''
    # Uno los DataFrames de juegos y reseñas en 'id'
    df_merged = pd.merge(df_games_f3, df_reviews_f3, left_on='id', right_on='item_id', how='inner')

    # Filtro por reseñas negativas y por el año especificado
    df_filtered = df_merged[(df_merged['recommend'] == False) & (df_merged['sentiment_analysis'] == 0) & 
                            (pd.to_datetime(df_merged['release_date'], errors= 'coerce').dt.year == año)]

    if not df_filtered.empty:
        # Agrupo por juego y contar las no recomendaciones
        bottom_games = df_filtered.groupby('app_name')['recommend'].count().reset_index()

        # Ordeno de forma ascendente y tomar los primeros 3
        bottom_games = bottom_games.sort_values(by='recommend', ascending=True).head(3)

        # Crear la estructura de retorno
        retorno = [{"Puesto {}".format(i+1): juego} for i, juego in enumerate(bottom_games['app_name'])]

        return retorno
    else:
        return {"mensaje": "No hay juegos menos recomendados para el año especificado"}
    
@app.get('/sentiment_analysis')
def sentiment_analysis(año: int):
    '''
    En esta funcion podras ingresar el año de tu interes y te devolvera segun el año que ingresaste, una
    lista con la cantidad de registros de reseñas de usuarios que se encuentran categorizados con un analisis
    de sentimiento. Es decir: Negative, Neutral, Positive
    '''
    # uno DataFrame games y reviews en 'id'
    df_merged = pd.merge(df_gamesf1, df_reviews_f3, left_on='id', right_on='item_id', how='inner')

    # Filtro por el año especificado
    df_filtered = df_merged[pd.to_datetime(df_merged['release_date'], errors='coerce').dt.year == año]

    if not df_filtered.empty:
        # Contar registros según el análisis de sentimiento
        sentiment_counts = df_filtered['sentiment_analysis'].value_counts().to_dict()

        # Mapear los valores para tener las etiquetas correspondientes
        sentiment_counts = {
            "Negative": sentiment_counts.get(0, 0),
            "Neutral": sentiment_counts.get(1, 0),
            "Positive": sentiment_counts.get(2, 0)
        }

        return sentiment_counts
    else:
        return {"mensaje": "No hay registros para el año especificado"}
    
<<<<<<< HEAD
def recomendacion_usuario(item_id: int):
    # Buscar el juego por su ID
    juego = df_games_ML[df_games_ML['id'] == item_id]
    
    if juego.empty:
        # Si no se encuentra el juego, devolver un error HTTP 404
        raise HTTPException(status_code=404, detail=f"No se encontró ningún juego con el ID '{item_id}'.")
    
    # Obtener las recomendaciones del juego
    recomendaciones = juego['recomendaciones'].iloc[0]
    
    return {"recomendaciones": recomendaciones}

@app.get("/recommendation/{item_id}")
async def get_item_recommendations(item_id: int):
    '''
    En esta funcion ingresamos como parametro el item de un juego existente y devolvera una lista 
    con los 5 juegos mas similares al ingresado.
    '''
    return recomendacion_usuario(item_id)

df_user_genre = pd.read_csv(r'DataApi/UserForGenre.csv')

def UserForGenre(genero: str):
    # Filtrar el DataFrame por el género especificado
    df_filtered = df_user_genre[df_user_genre['genres'].str.contains(genero, case=False, na=False)]

    if not df_filtered.empty:
        # Encontrar el usuario con más horas jugadas para el género dado
        user_max_hours = df_filtered.groupby('user_id')['hours_game'].sum().idxmax()

        # Calcular la acumulación de horas jugadas por año
        horas_por_año = df_filtered.groupby('year')['hours_game'].sum()
        horas_por_año = [{"Año": int(year), "Horas": horas} for year, horas in horas_por_año.items()]

        return {"Usuario con más horas jugadas para Género " + genero: user_max_hours, "Horas jugadas": horas_por_año}
    else:
        return {"mensaje": "No se encontraron datos para el género especificado"}

# Definir ruta y método HTTP
@app.get("/user_for_genre/{genero}")
async def get_user_for_genre(genero: str):
    '''
    En esta funcion podras ingresar un genero de tu interes, por ejemplo: Action,Casual,Indie,Simulation,
    Strategy y te devolvera el usuario que acumula mas horas jugadas y una lista de la acumulación de horas
    jugadas por año.
    '''
    try:
        return UserForGenre(genero)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))