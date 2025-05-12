library ieee;
use ieee.std_logic_1164.all;

entity bin2segs is
  port (
    -- host side
    en     : in std_logic;                      -- capacitacion
    bin    : in std_logic_vector(3 downto 0);   -- codigo binario
    dp     : in std_logic;                      -- punto
    -- leds side
    segs_n : out std_logic_vector(7 downto 0)   -- codigo 7-segmentos
  );
end bin2segs;

-------------------------------------------------------------------

architecture syn of bin2segs is
  signal segs : std_logic_vector(7 downto 0);
begin 

  segs(7) <= not dp; 
  with bin select
    segs(6 downto 0) <= 
      "0000001" when X"0",  -- 0
      "1001111" when X"1",  -- 1
      "0010010" when X"2",  -- 2
      "0000110" when X"3",  -- 3
      "1001100" when X"4",  -- 4
      "0100100" when X"5",  -- 5
      "0100000" when X"6",  -- 6
      "0001111" when X"7",  -- 7
      "0000000" when X"8",  -- 8
      "0001100" when X"9",  -- 9
      "0001000" when X"A",  -- A
      "1100000" when X"B",  -- B
      "0110001" when X"C",  -- C
      "1000010" when X"D",  -- D
      "0110000" when X"E",  -- E
      "0111000" when X"F",  -- F
      "1111111" when others;

      
  segs_n <= segs when en = '1' else (others => '1');

end syn;