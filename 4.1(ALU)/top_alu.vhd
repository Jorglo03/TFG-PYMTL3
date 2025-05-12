library ieee;
use ieee.std_logic_1164.all;

entity top_alu is
  port (
    sws    :  in std_logic_vector(15 downto 0);
    btnL   :  in std_logic;
    btnR   :  in std_logic;
    leds   : out std_logic_vector(15 downto 0);
    an_n   : out std_logic_vector(3 downto 0);  
    segs_n : out std_logic_vector(7 downto 0)
  );
end top_alu;

---------------------------------------------------------------------

library ieee;
use ieee.numeric_std.all;

architecture syn of top_alu is

  signal opCode  : std_logic_vector(1 downto 0); 
  signal leftOp  : std_logic_vector(7 downto 0);
  signal rightOp : std_logic_vector(7 downto 0);
  signal result  : std_logic_vector(7 downto 0);
  signal digit   : std_logic_vector(3 downto 0);
  
  component ALU_Custom
  port (
    clk : in std_logic;
    fn : in std_logic_vector(1 downto 0);
    in0: in std_logic_vector(7 downto 0);
    in1: in std_logic_vector(7 downto 0);
    result : out std_logic_vector(7 downto 0);
    reset: in std_logic
  );
  end component;
  
  component bin2segs 
  port (
    -- host side
    en     : in std_logic;                      -- capacitacion
    bin    : in std_logic_vector(3 downto 0);   -- codigo binario
    dp     : in std_logic;                      -- punto
    -- leds side
    segs_n : out std_logic_vector(7 downto 0)   -- codigo 7-segmentos
  );
  end component;
begin

  opCode  <= btnL & btnR;
  leftOp  <= sws(15 downto 8);
  rightOp <= sws(7 downto 0);
  
  ALU: ALU_Custom
  port map(clk => '1', fn => opCode, in0 => std_logic_vector(leftOp), in1 => std_logic_vector(rightOp), result => result, reset => '0');

  leds  <= "00000000" & result;
  digit <= std_logic_vector(result(3 downto 0)); 
    
  an_n  <= "1110";

  converter : bin2segs
  port map ( en => '1', bin => digit, dp => '0', segs_n => segs_n ); 
    
end syn;	