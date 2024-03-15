Proyecto Sistema de Recomendación de Videojuegos
Este proyecto tiene como objetivo crear un sistema de recomendación de videojuegos para usuarios, utilizando datos de la plataforma Steam, una plataforma multinacional de videojuegos.

Notebooks
El proyecto se encuentra organizado en tres cuadernos de Jupyter:

ETL (Extract, Transform, Load):

Este cuaderno contiene el proceso de extracción, transformación y carga de los datos de Steam. Aquí se realizan las operaciones necesarias para limpiar y preparar los datos para su análisis posterior.
EDA (Exploratory Data Analysis):

En este cuaderno se lleva a cabo el Análisis Exploratorio de Datos. Se exploran las características de los datos y se identifican patrones o tendencias importantes que puedan ser relevantes para el desarrollo del sistema de recomendación.
Desarrollo y Prueba de Funciones de la API:

Este cuaderno se centra en el desarrollo y prueba de las funciones que alimentarán la API del sistema de recomendación. Aquí se implementan y prueban las funciones especiales de la API, como la recomendación de usuarios por género, la búsqueda del año con más horas jugadas por género, etc.
Funciones Especiales de la API
El sistema de recomendación cuenta con varias funciones especiales que proporcionan información útil a los usuarios:

UserForGenre(genero: str):

Devuelve el usuario que acumula más horas jugadas para el género dado y una lista de la acumulación de horas jugadas por año.
PlayTimeGenre(genero: str):

Devuelve el año con más horas jugadas para el género dado.
UsersRecommend(año: int):

Devuelve el top 3 de juegos MÁS recomendados por usuarios para el año dado.
UsersNotRecommend(año: int):

Devuelve el top 3 de juegos MENOS recomendados por usuarios para el año dado.
sentiment_analysis(año: int):

Según el año de lanzamiento, devuelve una lista con la cantidad de registros de reseñas de usuarios categorizados con un análisis de sentimiento.
Estas funciones proporcionan información valiosa para ayudar a los usuarios a descubrir nuevos videojuegos y tomar decisiones informadas sobre sus compras.

¡Disfruta explorando el mundo de los videojuegos con nuestro sistema de recomendación!