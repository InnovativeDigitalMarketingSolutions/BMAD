import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { MobileComponent } from '../MobileComponent';

describe('MobileComponent', () => {
  it('renders correctly with default props', () => {
    const { getByText } = render(<MobileComponent />);
    
    expect(getByText('Mobile Component')).toBeTruthy();
    expect(getByText('Press Me')).toBeTruthy();
  });

  it('renders with custom title', () => {
    const customTitle = 'Custom Mobile Component';
    const { getByText } = render(<MobileComponent title={customTitle} />);
    
    expect(getByText(customTitle)).toBeTruthy();
  });

  it('calls onPress when button is pressed', async () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(<MobileComponent onPress={mockOnPress} />);
    
    const button = getByText('Press Me');
    fireEvent.press(button);
    
    await waitFor(() => {
      expect(mockOnPress).toHaveBeenCalledTimes(1);
    });
  });

  it('disables button when disabled prop is true', () => {
    const { getByText } = render(<MobileComponent disabled={true} />);
    
    const button = getByText('Disabled');
    expect(button).toBeTruthy();
  });

  it('shows disabled text when disabled', () => {
    const { getByText } = render(<MobileComponent disabled={true} />);
    
    expect(getByText('Disabled')).toBeTruthy();
  });

  it('does not call onPress when disabled', async () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <MobileComponent onPress={mockOnPress} disabled={true} />
    );
    
    const button = getByText('Disabled');
    fireEvent.press(button);
    
    await waitFor(() => {
      expect(mockOnPress).not.toHaveBeenCalled();
    });
  });
});

// Flutter Test Example
/*
import 'package:flutter_test/flutter_test.dart';
import 'package:your_app/mobile_component.dart';

void main() {
  group('MobileComponent Tests', () {
    testWidgets('renders correctly with default props', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: MobileComponent()));
      
      expect(find.text('Mobile Component'), findsOneWidget);
      expect(find.text('Press Me'), findsOneWidget);
    });

    testWidgets('calls onPressed when button is tapped', (WidgetTester tester) async {
      bool buttonPressed = false;
      
      await tester.pumpWidget(MaterialApp(
        home: MobileComponent(
          onPressed: () => buttonPressed = true,
        ),
      ));
      
      await tester.tap(find.text('Press Me'));
      await tester.pump();
      
      expect(buttonPressed, true);
    });

    testWidgets('shows disabled state correctly', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(
        home: MobileComponent(disabled: true),
      ));
      
      expect(find.text('Disabled'), findsOneWidget);
    });
  });
}
*/

// iOS Test Example
/*
import XCTest
@testable import YourApp

class MobileComponentTests: XCTestCase {
    func testInitialState() {
        let component = MobileComponentView()
        XCTAssertEqual(component.title, "Mobile Component")
        XCTAssertFalse(component.isDisabled)
    }
    
    func testButtonAction() {
        let component = MobileComponentView()
        var actionCalled = false
        
        component.onButtonClick = {
            actionCalled = true
        }
        
        component.buttonTapped()
        XCTAssertTrue(actionCalled)
    }
    
    func testDisabledState() {
        let component = MobileComponentView()
        component.isDisabled = true
        
        XCTAssertTrue(component.isDisabled)
        XCTAssertEqual(component.buttonTitle, "Disabled")
    }
}
*/

// Android Test Example
/*
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.rule.ActivityTestRule
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MobileComponentTest {
    @get:Rule
    val activityRule = ActivityTestRule(MobileComponentActivity::class.java)
    
    @Test
    fun testInitialState() {
        onView(withId(R.id.titleTextView))
            .check(matches(withText("Mobile Component")))
        
        onView(withId(R.id.actionButton))
            .check(matches(withText("Press Me")))
    }
    
    @Test
    fun testButtonClick() {
        onView(withId(R.id.actionButton))
            .perform(click())
        
        // Verify the action was performed
        // This depends on your implementation
    }
}
*/ 