package com.energiai.repository;

import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

import com.energiai.entity.AnalisisEnergeticoEntity;

public interface AnalisisEnergeticoRepository extends JpaRepository<AnalisisEnergeticoEntity, UUID> {
}
