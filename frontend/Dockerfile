FROM nginx:alpine
LABEL org.opencontainers.image.authors="Nils Ost"
COPY --from=nilsost/nlpt-kiosk-controller-frontend-build:helper /app/dist/nlpt-kiosk/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
