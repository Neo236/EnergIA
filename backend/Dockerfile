# ==========================================
# Dockerfile Backend - Java 17 Spring Boot
# ==========================================
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

COPY analisis-energetico-api/pom.xml .
COPY analisis-energetico-api/.mvn .mvn
COPY analisis-energetico-api/mvnw .
COPY analisis-energetico-api/mvnw.cmd .

RUN ./mvnw dependency:go-offline -B || true

COPY analisis-energetico-api/src ./src

RUN ./mvnw clean package -DskipTests

# ==========================================
# Runtime Stage
# ==========================================
FROM eclipse-temurin:25-jre AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appgroup && useradd --system --gid appgroup appuser

COPY --from=builder /app/target/*.jar app.jar
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8080

ENV PORT=8080 \
    SPRING_PROFILES_ACTIVE=prod \
    JAVA_OPTS="-XX:+UseG1GC -XX:MaxRAMPercentage=75.0 -Duser.timezone=UTC"

# Se apunta a /actuator/health/readiness, no a /actuator/health: readiness
# incluye el indicador db (ver application.properties), asi que `docker compose
# ps` refleja si el contenedor puede realmente atender trafico y no solo si la
# JVM esta viva. wget devuelve != 0 ante el 503 que emite un grupo DOWN.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/actuator/health/readiness || exit 1

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
