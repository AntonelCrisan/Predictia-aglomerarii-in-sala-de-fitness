USE aglomerare_sali;
CREATE TABLE sali (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(100) NOT NULL,
    judet VARCHAR(100),
    localitate VARCHAR(100),
    adresa VARCHAR(255),
    program_lucru VARCHAR(255)
);
CREATE TABLE utilizatori (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    parola VARCHAR(255) NOT NULL,
    id_sala INT,
    FOREIGN KEY (id_sala) REFERENCES sali(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE date_colectate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numar_oameni INT NOT NULL,
    zi TINYINT NOT NULL,
    luna TINYINT NOT NULL,
    an SMALLINT NOT NULL,
    e_weekend BOOLEAN DEFAULT 0,
    e_vacanta BOOLEAN DEFAULT 0,
    temperatura DECIMAL(5,2),
    e_inceput_de_semestru BOOLEAN DEFAULT 0,
    e_semestru_in_derulare BOOLEAN DEFAULT 0,
    ora TIME NOT NULL,
    id_sala INT NOT NULL,
    FOREIGN KEY (id_sala) REFERENCES sali(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE aparate_picioare (
    id INT AUTO_INCREMENT PRIMARY KEY,
    leg_press BOOLEAN DEFAULT 0,
    hack_squat BOOLEAN DEFAULT 0,
    leg_extension BOOLEAN DEFAULT 0,
    leg_curl BOOLEAN DEFAULT 0,
    hip_thrust BOOLEAN DEFAULT 0,
    abductor_machine BOOLEAN DEFAULT 0,
    adductor_machine BOOLEAN DEFAULT 0
);
CREATE TABLE aparate_spate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lat_pulldown BOOLEAN DEFAULT 0,
    seated_row_machine BOOLEAN DEFAULT 0,
    back_extension BOOLEAN DEFAULT 0
);
CREATE TABLE aparate_piept (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chest_press BOOLEAN DEFAULT 0,
    pec_deck BOOLEAN DEFAULT 0,
    incline_chest_press BOOLEAN DEFAULT 0
);
CREATE TABLE aparate_umeri (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shoulder_press BOOLEAN DEFAULT 0,
    lateral_raises BOOLEAN DEFAULT 0
);
CREATE TABLE aparate_brate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    biceps_curl BOOLEAN DEFAULT 0,
    triceps_push_down BOOLEAN DEFAULT 0
);
CREATE TABLE aparate_abdomen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ab_crunch BOOLEAN DEFAULT 0,
    rotary_torso BOOLEAN DEFAULT 0
);

CREATE TABLE aparate_full_body (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cable_crossover BOOLEAN DEFAULT 0
);


CREATE TABLE sala_aparate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_aparate_picioare INT,
    id_aparate_spate INT,
    id_aparate_piept INT,
    id_aparate_umeri INT,
    id_aparate_brate INT,
    id_aparate_abdomen INT,
    id_aparate_full_body INT,
    id_sala INT NOT NULL,
    FOREIGN KEY (id_sala) REFERENCES sali(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_aparate_picioare) REFERENCES aparate_picioare(id),
    FOREIGN KEY (id_aparate_spate) REFERENCES aparate_spate(id),
    FOREIGN KEY (id_aparate_piept) REFERENCES aparate_piept(id),
    FOREIGN KEY (id_aparate_umeri) REFERENCES aparate_umeri(id),
    FOREIGN KEY (id_aparate_brate) REFERENCES aparate_brate(id),
    FOREIGN KEY (id_aparate_abdomen) REFERENCES aparate_abdomen(id),
    FOREIGN KEY (id_aparate_full_body) REFERENCES aparate_full_body(id)
);
