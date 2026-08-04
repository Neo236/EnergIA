package com.energiai.config;                                                                                                                                                  
                                                                                                                                                                                  
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;                                                                                                                  
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

@Configuration
public class MlClientConfig {
    
    @Value("${ml.service.connect-timeout:3000}")
    private int connectTimeout;

    @Value("${ml.service.read-timeout:5000}")
    private int readTimeout;

    @Bean
    public RestClient restClient() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(connectTimeout);
        factory.setReadTimeout(readTimeout);

        return RestClient.builder()
                .requestFactory(factory)
                .build();
    }
}   