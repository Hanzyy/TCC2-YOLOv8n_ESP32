#include <Arduino.h>

// ==========================
// VIA A
// ==========================
#define VERDE_A 27
#define AMARELO_A 26
#define VERMELHO_A 25

// ==========================
// VIA B
// ==========================
#define VERDE_B 21
#define AMARELO_B 19
#define VERMELHO_B 18

// ==========================
// PEDESTRES
// ==========================
#define PED_A_VERDE 33
#define PED_A_VERMELHO 32

#define PED_B_VERDE 23
#define PED_B_VERMELHO 22

// ==========================
// BOTÕES
// ==========================
#define BOTAO_A 4
#define BOTAO_B 5

// ==========================
// TEMPOS
// ==========================

// tempo sem receber sinal (ms)
unsigned long tempoSemSinal = 5000;

// tempo mínimo verde (ms)
unsigned long tempoMinimoVerde = 5000;

// tempo amarelo (ms)
unsigned long tempoAmarelo = 2000;

// tempo máximo verde (ms)
unsigned long tempoMaximoVerde = 15000;

// tempo pedestre (ms)
unsigned long tempoPedestre = 5000;

// ==========================
// ESTADOS
// ==========================

char viaAtual = 'A';

unsigned long ultimoSinalA = 0;
unsigned long ultimoSinalB = 0;

unsigned long inicioVerde = 0;

bool pedidoPedestre = false;

// ==========================
// FUNÇÕES
// ==========================

void delayBotao(int tempo) 
{ 
    unsigned long inicio = millis(); 
    while (millis() - inicio < tempo) 
    { 
        if (digitalRead(BOTAO_A) == LOW || digitalRead(BOTAO_B) == LOW) 
        { 
            pedidoPedestre = true; 
        } 
        delay(10); 
    } 
}

void fecharTudo()
{
    digitalWrite(VERDE_A, LOW);
    digitalWrite(AMARELO_A, LOW);
    digitalWrite(VERMELHO_A, HIGH);

    digitalWrite(VERDE_B, LOW);
    digitalWrite(AMARELO_B, LOW);
    digitalWrite(VERMELHO_B, HIGH);
}

void abrirViaA()
{
    fecharTudo();

    digitalWrite(VERMELHO_A, LOW);
    digitalWrite(VERDE_A, HIGH);

    viaAtual = 'A';

    inicioVerde = millis();

    Serial.println("Via A aberta");
}

void abrirViaB()
{
    fecharTudo();

    digitalWrite(VERMELHO_B, LOW);
    digitalWrite(VERDE_B, HIGH);

    viaAtual = 'B';

    inicioVerde = millis();

    Serial.println("Via B aberta");
}

void amarelarViaA()
{
    digitalWrite(VERDE_A, LOW);
    digitalWrite(AMARELO_A, HIGH);

    delayBotao(tempoAmarelo);

    digitalWrite(AMARELO_A, LOW);
    digitalWrite(VERMELHO_A, HIGH);
}

void amarelarViaB()
{
    digitalWrite(VERDE_B, LOW);
    digitalWrite(AMARELO_B, HIGH);

    delayBotao(tempoAmarelo);

    digitalWrite(AMARELO_B, LOW);
    digitalWrite(VERMELHO_B, HIGH);
}

void liberarPedestres()
{
    fecharTudo();

    digitalWrite(PED_A_VERMELHO, LOW);
    digitalWrite(PED_B_VERMELHO, LOW);

    digitalWrite(PED_A_VERDE, HIGH);
    digitalWrite(PED_B_VERDE, HIGH);

    delayBotao(tempoPedestre);

    digitalWrite(PED_A_VERDE, LOW);
    digitalWrite(PED_B_VERDE, LOW);

    digitalWrite(PED_A_VERMELHO, HIGH);
    digitalWrite(PED_B_VERMELHO, HIGH);

    pedidoPedestre = false;

    if (viaAtual == 'A')
        abrirViaA();
    else
        abrirViaB();
}

void resetSistema()
{
    Serial.println("RESET SISTEMA");

    fecharTudo();

    digitalWrite(PED_A_VERDE, LOW);
    digitalWrite(PED_B_VERDE, LOW);

    digitalWrite(PED_A_VERMELHO, HIGH);
    digitalWrite(PED_B_VERMELHO, HIGH);

    pedidoPedestre = false;

    ultimoSinalA = millis();
    ultimoSinalB = millis();

    inicioVerde = millis();

    abrirViaA();
}

// ==========================
// SETUP
// ==========================

void setup()
{
    Serial.begin(115200);

    pinMode(VERDE_A, OUTPUT);
    pinMode(AMARELO_A, OUTPUT);
    pinMode(VERMELHO_A, OUTPUT);

    pinMode(VERDE_B, OUTPUT);
    pinMode(AMARELO_B, OUTPUT);
    pinMode(VERMELHO_B, OUTPUT);

    pinMode(PED_A_VERDE, OUTPUT);
    pinMode(PED_A_VERMELHO, OUTPUT);

    pinMode(PED_B_VERDE, OUTPUT);
    pinMode(PED_B_VERMELHO, OUTPUT);

    pinMode(BOTAO_A, INPUT_PULLUP);
    pinMode(BOTAO_B, INPUT_PULLUP);

    digitalWrite(PED_A_VERMELHO, HIGH);
    digitalWrite(PED_B_VERMELHO, HIGH);

    abrirViaA();
}

// ==========================
// LOOP
// ==========================

void loop()
{
    // RECEBE SERIAL

    if (Serial.available())
    {
        char comando = Serial.read();

        if (comando == 'A')
        {
            ultimoSinalA = millis();
        }
        else if (comando == 'B')
        {
            ultimoSinalB = millis();
        }
        else if (comando == 'P')
        {
            pedidoPedestre = true;
        }
        else if (comando == 'R')
        {
            resetSistema();
        }
    }

    // BOTÕES PEDESTRE

    if (digitalRead(BOTAO_A) == LOW ||
        digitalRead(BOTAO_B) == LOW)
    {
        pedidoPedestre = true;
    }

    // TEMPO MÍNIMO DE VERDE

    if (millis() - inicioVerde < tempoMinimoVerde)
    {
        return;
    }

    // VIA A ABERTA

    if (viaAtual == 'A')
    {
        bool semSinal =
            millis() - ultimoSinalA > tempoSemSinal;

        bool tempoMaximo =
            millis() - inicioVerde > tempoMaximoVerde;

        if (semSinal || tempoMaximo)
            {
                amarelarViaA();

                if (pedidoPedestre)
                {
                    liberarPedestres();

                    abrirViaB();
                }
                else
                {
                    abrirViaB();
                }
            }
        }

    // VIA B ABERTA

    else if (viaAtual == 'B')
    {
        bool semSinal =
            millis() - ultimoSinalB > tempoSemSinal;

        bool tempoMaximo =
            millis() - inicioVerde > tempoMaximoVerde;

        if (semSinal || tempoMaximo)
        {
            amarelarViaB();

            if (pedidoPedestre)
            {
                liberarPedestres();

                abrirViaA();
            }
            else
            {
                abrirViaA();
            }
        }
    }
}