package com.energiai.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/analisis-energetico")
public class AnalisisEnergeticoController {
    
    @GetMapping("/test")
    public String test() {
        return "API de análisis energético funcionando correctamente.";
    }

}