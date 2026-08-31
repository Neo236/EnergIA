package com.energia.repository;

import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

import com.energia.entity.AnalisisEnergeticoEntity;

public interface AnalisisEnergeticoRepository extends JpaRepository<AnalisisEnergeticoEntity, UUID> {
}
